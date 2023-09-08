
from Models.Stream import StreamDecoder, StreamEncoder
from dataclasses import dataclass

@dataclass
class Beatmap:
    artist: str=""
    title: str=""
    creator: str=""
    version: str=""
    hash: str=""
    filename: str=""
    status: int=0
    circles: int=0
    sliders: int=0
    spinners: int=0
    ar: float=0
    cs: float=0
    hp: float=0
    od: float=0
    drain: int=0
    length: int=0
    beatmap_id: int=0
    beatmapset_id: int=0
    mode: int=0
    source: str=""
    tags: str=""
    foldername: str=""
    leeway: float=-1 # Set externally
    missing: bool=False

    def __hash__(self) -> int:
        return hash(self.hash)

    def search(self) -> str:
        return f"{self.artist} - {self.title} [{self.version}] {self.creator} {self.beatmap_id} {self.beatmapset_id} {self.source} {self.tags}".lower()

    @staticmethod
    def convert_status(online_status: int) -> int:
        if online_status == 1: return 4
        if online_status == 2: return 5
        if online_status == 3: return 6
        if online_status == 3: return 7
        return 2

    @classmethod
    def decode_database(cls, bytestream):
        # https://github.com/ppy/osu/wiki/Legacy-database-file-structure
        artist = StreamDecoder.ulebstring(bytestream)
        StreamDecoder.ulebsstring(bytestream)
        title = StreamDecoder.ulebstring(bytestream)
        StreamDecoder.ulebsstring(bytestream)
        creator = StreamDecoder.ulebstring(bytestream)
        version = StreamDecoder.ulebstring(bytestream)
        StreamDecoder.ulebsstring(bytestream)
        hash = StreamDecoder.ulebstring(bytestream)
        filename = StreamDecoder.ulebstring(bytestream)
        status = StreamDecoder.byte(bytestream)
        circles = StreamDecoder.short(bytestream)
        sliders = StreamDecoder.short(bytestream)
        spinners = StreamDecoder.short(bytestream)
        bytestream.seek(8, 1)
        ar = StreamDecoder.single(bytestream)
        cs = StreamDecoder.single(bytestream)
        hp = StreamDecoder.single(bytestream)
        od = StreamDecoder.single(bytestream)
        bytestream.seek(8, 1)
        osu_stars_count = StreamDecoder.int(bytestream)
        bytestream.seek(14 * osu_stars_count, 1)
        taiko_stars_count = StreamDecoder.int(bytestream)
        bytestream.seek(14 * taiko_stars_count, 1)
        catch_stars_count = StreamDecoder.int(bytestream)
        bytestream.seek(14 * catch_stars_count, 1)
        mania_stars_count = StreamDecoder.int(bytestream)
        bytestream.seek(14 * mania_stars_count, 1)
        drain = StreamDecoder.int(bytestream)
        length = StreamDecoder.int(bytestream)
        bytestream.seek(4, 1)
        timing_points_count = StreamDecoder.int(bytestream)
        bytestream.seek(17 * timing_points_count, 1)
        beatmap_id = StreamDecoder.int(bytestream)
        beatmapset_id = StreamDecoder.int(bytestream)
        bytestream.seek(14, 1)
        mode = StreamDecoder.byte(bytestream)
        source = StreamDecoder.ulebstring(bytestream)
        tags = StreamDecoder.ulebstring(bytestream)
        bytestream.seek(2, 1)
        StreamDecoder.ulebsstring(bytestream)
        bytestream.seek(10, 1)
        foldername = StreamDecoder.ulebstring(bytestream)
        bytestream.seek(18, 1)

        return cls(
            artist,
            title,
            creator,
            version,
            hash,
            filename,
            status,
            circles,
            sliders,
            spinners,
            ar,
            cs,
            hp,
            od,
            drain,
            length,
            beatmap_id,
            beatmapset_id,
            mode,
            source,
            tags,
            foldername,
        )

    @classmethod
    def decode_beatmap_db_hash(cls, bytestream, database):
        hash = StreamDecoder.ulebstring(bytestream)
        if hash in database.by_hash:
            return database.by_hash[hash]

        beatmap_id = 0
        if hash.startswith("semiRandomHash:"):
            beatmap_id = int(hash.split(':')[1].split('|')[0])
            if beatmap_id in database.by_id:
                return database.by_id[beatmap_id]

        return cls(
            beatmap_id=beatmap_id,
            hash=hash,
            missing=True,
        )

    @classmethod
    def decode_beatmap_osdb_hash(cls, bytestream, database):
        hash = StreamDecoder.string(bytestream)
        if hash in database.by_hash:
            return database.by_hash[hash]

        beatmap_id = 0
        if hash.startswith("semiRandomHash:"):
            beatmap_id = int(hash.split(':')[1].split('|')[0])
            if beatmap_id in database.by_id:
                return database.by_id[beatmap_id]

        return cls(
            beatmap_id=beatmap_id,
            hash=hash,
            missing=True,
        )

    @classmethod
    def decode_beatmap_osdb(cls, bytestream, database):
        beatmap_id = StreamDecoder.int(bytestream)
        beatmapset_id = StreamDecoder.int(bytestream)
        artist = StreamDecoder.string(bytestream)
        title = StreamDecoder.string(bytestream)
        version = StreamDecoder.string(bytestream)
        hash = StreamDecoder.string(bytestream)
        StreamDecoder.sstring(bytestream)
        mode = StreamDecoder.byte(bytestream)
        bytestream.seek(8, 1)

        if hash in database.by_hash:
            return database.by_hash[hash]

        return cls(
            artist=artist,
            title=title,
            version=version,
            hash=hash,
            beatmap_id=beatmap_id,
            beatmapset_id=beatmapset_id,
            mode=mode,
            missing=True,
        )

    @classmethod
    def decode_beatmap_id(cls, beatmap_id, database):
        if beatmap_id in database.by_id:
            return database.by_id[beatmap_id]

        return cls(
            beatmap_id=beatmap_id,
            hash=f"semiRandomHash:{beatmap_id}|0",
            missing=True,
        )

    @classmethod
    def decode_beatmap_hash(cls, hash, database):
        if hash in database.by_hash:
            return database.by_hash[hash]

        return cls(
            hash=hash,
            missing=True,
        )

    @classmethod
    def from_ossapi(cls, score, database):
        artist = score.beatmapset.artist
        title = score.beatmapset.title
        creator = score.beatmapset.creator
        version = score.beatmap.version
        hash = score.beatmap.checksum
        status = cls.convert_status(score.beatmap.status)
        circles = score.beatmap.count_circles
        sliders = score.beatmap.count_sliders
        spinners = score.beatmap.count_spinners
        ar = score.beatmap.ar
        cs = score.beatmap.cs
        hp = score.beatmap.drain
        od = score.beatmap.accuracy
        drain = int(score.beatmap.drain)
        length = score.beatmap.hit_length
        beatmap_id = score.beatmap.id
        beatmapset_id = score.beatmapset.id
        mode = score.beatmap.mode_int
        source = score.beatmapset.source

        if hash in database.by_hash:
            return database.by_hash[hash]

        return cls(
            artist=artist,
            title=title,
            creator=creator,
            version=version,
            hash=hash,
            status=status,
            circles=circles,
            sliders=sliders,
            spinners=spinners,
            ar=ar,
            cs=cs,
            hp=hp,
            od=od,
            drain=drain,
            length=length,
            beatmap_id=beatmap_id,
            beatmapset_id=beatmapset_id,
            mode=mode,
            source=source,
            missing=True
        )

    @classmethod
    def from_osustats(cls, score, database):
        artist = score['beatmap']['artist']
        title = score['beatmap']['title']
        creator = score['beatmap']['creator']
        version = score['beatmap']['version']
        status = cls.convert_status(score['beatmap']['approved'])
        ar = score['beatmap']['diffApproach']
        cs = score['beatmap']['diffSize']
        hp = score['beatmap']['diffDrain']
        od = score['beatmap']['diffOverall']
        drain = score['beatmap']['hitLength']
        length =  score['beatmap']['totalLength']
        beatmap_id = score['beatmap']['beatmapId']
        beatmapset_id = score['beatmap']['beatmapSetId']
        mode = score['beatmap']['mode']
        source = score['beatmap']['source']

        if beatmap_id in database.by_id:
            return database.by_id[beatmap_id]

        return cls(
            artist=artist,
            title=title,
            creator=creator,
            version=version,
            hash=f"semiRandomHash:{beatmap_id}|0",
            status=status,
            ar=ar,
            cs=cs,
            hp=hp,
            od=od,
            drain=drain,
            length=length,
            beatmap_id=beatmap_id,
            beatmapset_id=beatmapset_id,
            mode=mode,
            source=source,
            missing=True
        )

    def encode_beatmap_hash(self, bytestream) -> None:
        StreamEncoder.ulebstring(self.hash, bytestream)

    def encode_beatmap_osdb_hash(self, bytestream) -> None:
        StreamEncoder.string(self.hash, bytestream)

    def encode_beatmap_osdb(self, bytestream) -> None:
        StreamEncoder.int(self.beatmap_id, bytestream)
        StreamEncoder.int(self.beatmapset_id, bytestream)
        StreamEncoder.string(self.artist, bytestream)
        StreamEncoder.string(self.title, bytestream)
        StreamEncoder.string(self.version, bytestream)
        StreamEncoder.string(self.hash, bytestream)
        StreamEncoder.byte(0, bytestream)
        StreamEncoder.byte(self.mode, bytestream)
        StreamEncoder.int(0, bytestream)
        StreamEncoder.int(0, bytestream)
