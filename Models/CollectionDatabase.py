
from Models.Collection import Collection
from Models.BeatmapDatabase import BeatmapDatabase
from Models.Stream import StreamDecoder, StreamEncoder
from dataclasses import dataclass
from typing import List
from io import BytesIO
import zlib

@dataclass(init=False)
class CollectionDatabase:
    collections: List[Collection]
    database: BeatmapDatabase

    def __init__(self) -> None:
        self.collections = []
        self.database = BeatmapDatabase()

    def __len__(self) -> int:
        return len(self.collections)

    def clear(self) -> None:
        self.collections = []

    def insert(self, index, collection) -> None:
        self.collections.insert(index, collection)

    def append(self, collection) -> None:
        self.collections.append(collection)

    def delete(self, indices) -> None:
        for index in indices[::-1]:
            self.collections.pop(index)

    def duplicate(self, indices, name) -> None:
        for index in indices[::-1]:
            old = self.collections[index]
            beatmaps = old.beatmaps.copy()
            collection = Collection(name.format(old.name), beatmaps)
            self.insert(index + 1, collection)

    def invert(self, indices, name) -> None:
        for index in indices[::-1]:
            old = self.collections[index]
            beatmaps = self.database.beatmaps() - old.beatmaps
            collection = Collection(name.format(old.name), beatmaps)
            self.insert(index + 1, collection)

    def subtract(self, index1, index2, name) -> None:
        old1, old2 = self.collections[index1], self.collections[index2]
        beatmaps = old1.beatmaps.copy() - old2.beatmaps.copy()
        collection = Collection(name.format(old1.name, old2.name), beatmaps)
        self.insert(index1 + 1, collection)

    def merge(self, indices, name) -> None:
        beatmaps = self.collections[indices[0]].beatmaps.copy()
        for index in indices[1:]:
            old = self.collections[index]
            beatmaps = beatmaps.union(old.beatmaps)
        collection = Collection(name.format(len(indices)), beatmaps)
        self.insert(indices[-1] + 1, collection)

    def intersect(self, indices, name) -> None:
        beatmaps = self.collections[indices[0]].beatmaps.copy()
        for index in indices[1:]:
            old = self.collections[index]
            beatmaps = beatmaps.intersection(old.beatmaps)
        collection = Collection(name.format(len(indices)), beatmaps)
        self.insert(indices[-1] + 1, collection)

    def load_file(self, filepath) -> None:
        if filepath.endswith(".db"):
            with open(filepath, 'rb') as db:
                self.decode_collection_db(db)
        elif filepath.endswith(".osdb"):
            with open(filepath, 'rb') as db:
                self.decode_collection_osdb(db)
        elif filepath.endswith(".txt"):
            with open(filepath, 'r') as db:
                self.decode_collection_text(db)

    def load_database(self, filepath) -> None:
        self.database.load_file(filepath)

    def save_file(self, filepath) -> None:
        if filepath.endswith(".db"):
            with open(filepath, 'wb') as db:
                self.encode_collection_db(db)
        elif filepath.endswith(".osdb"):
            with open(filepath, 'wb') as db:
                self.encode_collection_osdb(db)

    def decode_collection_db(self, bytestream) -> None:
        bytestream.seek(4, 1)
        collection_count = StreamDecoder.int(bytestream)
        self.collections += [Collection._decode_collection_db(bytestream, self.database) for _ in range(collection_count)]

    def decode_collection_osdb(self, bytestream) -> None:
        version = StreamDecoder.string(bytestream)
        if version != "o!dm8":
            raise ValueError("osdb version not supported")
        gzip = zlib.decompressobj(wbits=zlib.MAX_WBITS|16)
        gzip_bytestream = BytesIO(gzip.decompress(bytestream.read()))
        StreamDecoder.sstring(gzip_bytestream)
        gzip_bytestream.seek(8, 1)
        StreamDecoder.sstring(gzip_bytestream)
        collection_count = StreamDecoder.int(gzip_bytestream)
        self.collections += [Collection._decode_collection_osdb(gzip_bytestream, self.database) for _ in range(collection_count)]

    def decode_collection_text(self, filestream) -> None:
        self.collections.append(Collection._decode_beatmap_ids(filestream, self.database))

    def encode_collection_db(self, bytestream) -> None:
        StreamEncoder.int(20230727, bytestream)
        StreamEncoder.int(len(self.collections), bytestream)
        for collection in self.collections:
            collection._encode_collection_db(bytestream)

    def encode_collection_osdb(self, bytestream) -> None:
        StreamEncoder.string("o!dm8", bytestream)
        gzip_bytestream = BytesIO(b'')
        StreamEncoder.string("o!dm8", gzip_bytestream)
        StreamEncoder.int(0, gzip_bytestream)
        StreamEncoder.int(0, gzip_bytestream)
        StreamEncoder.string("N/A", gzip_bytestream)
        StreamEncoder.int(len(self.collections), gzip_bytestream)
        for collection in self.collections:
            collection._encode_collection_osdb(gzip_bytestream)
        StreamEncoder.string("By Piotrekol", gzip_bytestream)
        gzip = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        gzip_data = gzip.compress(gzip_bytestream.getvalue()) + gzip.flush()
        bytestream.write(gzip_data)
