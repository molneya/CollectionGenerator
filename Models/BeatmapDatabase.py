
from Models.Beatmap import Beatmap
from Models.Stream import StreamDecoder
from dataclasses import dataclass
from typing import Dict, Set

@dataclass(init=False)
class BeatmapDatabase:
    by_hash: Dict[str, Beatmap]
    by_id: Dict[int, Beatmap]

    def __init__(self) -> None:
        self.by_hash = {}
        self.by_id = {}

    def __len__(self) -> int:
        return len(self.by_hash)

    def is_empty(self) -> bool:
        return len(self) == 0

    def beatmaps(self) -> Set[Beatmap]:
        return set(self.by_hash.values())

    def load_file(self, filepath) -> None:
        with open(filepath, 'rb') as db:
            self.decode(db)

    def decode(self, bytestream) -> None:
        bytestream.seek(17, 1)
        StreamDecoder.ulebsstring(bytestream)
        beatmap_count = StreamDecoder.int(bytestream)
        for _ in range(beatmap_count):
            beatmap = Beatmap.decode_database(bytestream)
            # Hashes should be unique, but do this check anyway
            if beatmap.hash not in self.by_hash:
                self.by_hash[beatmap.hash] = beatmap
            # IDs are not unique, replace with current if better status
            if beatmap.beatmap_id not in self.by_id:
                self.by_id[beatmap.beatmap_id] = beatmap
            elif self.by_id[beatmap.beatmap_id].status < beatmap.status:
                self.by_id[beatmap.beatmap_id] = beatmap
