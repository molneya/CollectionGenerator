
from Models.Beatmap import Beatmap
from Models.Stream import StreamDecoder, StreamEncoder
from dataclasses import dataclass
from typing import Set
from io import BytesIO
import zlib

@dataclass(init=False)
class Collection:
    name: str
    beatmaps: Set[Beatmap]
    missing: int

    def __init__(self, name, beatmaps) -> None:
        self.name = name
        self.beatmaps = beatmaps
        self.missing = sum([beatmap.missing for beatmap in beatmaps])

    def __len__(self) -> int:
        return len(self.beatmaps)

    def save_file(self, filepath) -> None:
        if filepath.endswith(".db"):
            with open(filepath, 'wb') as db:
                self.encode_collection_db(db)
        elif filepath.endswith(".osdb"):
            with open(filepath, 'wb') as db:
                self.encode_collection_osdb(db)

    def encode_collection_db(self, bytestream) -> None:
        StreamEncoder.int(20230727, bytestream)
        StreamEncoder.int(1, bytestream)
        self._encode_collection_db(bytestream)

    def encode_collection_osdb(self, bytestream) -> None:
        StreamEncoder.string("o!dm8", bytestream)
        gzip_bytestream = BytesIO(b'')
        StreamEncoder.string("o!dm8", gzip_bytestream)
        StreamEncoder.int(0, gzip_bytestream)
        StreamEncoder.int(0, gzip_bytestream)
        StreamEncoder.string("N/A", gzip_bytestream)
        StreamEncoder.int(1, gzip_bytestream)
        self._encode_collection_osdb(gzip_bytestream)
        StreamEncoder.string("By Piotrekol", gzip_bytestream)
        gzip = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        gzip_data = gzip.compress(gzip_bytestream.getvalue()) + gzip.flush()
        bytestream.write(gzip_data)

    @classmethod
    def _decode_collection_db(cls, bytestream, database):
        # Does not decode header. Not intended to be used by itself.
        name = StreamDecoder.ulebstring(bytestream)
        beatmap_count = StreamDecoder.int(bytestream)
        beatmaps = [Beatmap.decode_beatmap_db_hash(bytestream, database) for _ in range(beatmap_count)]
        return cls(name, set(beatmaps))

    @classmethod
    def _decode_collection_osdb(cls, bytestream, database):
        # Does not decode header. Not intended to be used by itself.
        name = StreamDecoder.string(bytestream)
        bytestream.seek(4, 1)
        full_count = StreamDecoder.int(bytestream)
        beatmaps = [Beatmap.decode_beatmap_osdb(bytestream, database) for _ in range(full_count)]
        hash_count = StreamDecoder.int(bytestream)
        beatmaps += [Beatmap.decode_beatmap_osdb_hash(bytestream, database) for _ in range(hash_count)]
        return cls(name, set(beatmaps))

    @classmethod
    def _decode_beatmap_ids(cls, filestream, database):
        # Doesn't do anything special on its own that requires it to be private, but I like conformity
        beatmaps = []
        for line in filestream.splitlines():
            # clean string by only getting digit characters
            beatmap_id = int(''.join(chr for chr in line if chr.isdigit()))
            beatmaps += [Beatmap.decode_beatmap_id(beatmap_id, database)]
        return cls(filestream.name, set(beatmaps))

    def _encode_collection_db(self, bytestream) -> None:
        # Does not encode header. Not intended to be used by itself.
        StreamEncoder.ulebstring(self.name, bytestream)
        StreamEncoder.int(len(self.beatmaps), bytestream)
        for beatmap in self.beatmaps:
            beatmap.encode_beatmap_hash(bytestream)

    def _encode_collection_osdb(self, bytestream) -> None:
        # Does not encode header. Not intended to be used by itself.
        full_beatmaps = list(filter(lambda b: not b.missing, self.beatmaps))
        hash_only_beatmaps = list(filter(lambda b: b.missing, self.beatmaps))
        StreamEncoder.string(self.name, bytestream)
        StreamEncoder.int(0, bytestream)
        StreamEncoder.int(len(full_beatmaps), bytestream)
        for beatmap in full_beatmaps:
            beatmap.encode_beatmap_osdb(bytestream)
        StreamEncoder.int(len(hash_only_beatmaps), bytestream)
        for beatmap in hash_only_beatmaps:
            beatmap.encode_beatmap_osdb_hash(bytestream)
