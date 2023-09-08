
from Models.Beatmap import Beatmap
from Models.Stream import StreamDecoder
from dataclasses import dataclass
from ossapi import Mod

@dataclass
class Score:
    beatmap: Beatmap
    mode: int=0
    user: str=""
    greats: int=0
    oks: int=0
    mehs: int=0
    perfects: int=0 # Geki
    goods: int=0 # Katu
    misses: int=0
    score: int=0
    combo: int=0
    perfect: bool=False
    mods: str=""
    accuracy: float=1.0
    grade: str=""

    def __post_init__(self) -> None:
        self.accuracy = self.get_accuracy()
        self.grade = self.get_grade().lower()

    def get_accuracy(self) -> float:
        if self.mode == 0:
            total = self.greats + self.oks + self.mehs + self.misses
            if total == 0:
                return 1.0
            return (300 * self.greats + 100 * self.oks + 50 * self.mehs) / (300 * total)
        if self.mode == 1:
            total = self.greats + self.oks + self.misses
            if total == 0:
                return 1.0
            return (300 * self.greats + 150 * self.oks) / (300 * total)
        if self.mode == 2:
            total = self.greats + self.oks + self.mehs + self.misses + self.goods
            if total == 0:
                return 1.0
            return (self.greats + self.oks + self.mehs) / (total)
        if self.mode == 3:
            total = self.perfects + self.greats + self.goods + self.oks + self.mehs + self.misses
            if total == 0:
                return 1.0
            return (300 * (self.perfects + self.greats) + 200 * self.goods + 100 * self.oks + 50 * self.mehs) / (300 * total)

    def get_grade(self) -> str:
        grade = "D"
        if self.mode in [0, 1]:
            total = self.greats + self.oks + self.mehs + self.misses
            if (self.greats == total): grade = "SS"
            elif (self.greats / total > 0.9) and (self.mehs / total < 0.01) and (self.misses == 0): grade = "S"
            elif ((self.greats / total > 0.8) and (self.misses == 0)) or (self.greats / total > 0.9): grade = "A"
            elif ((self.greats / total > 0.7) and (self.misses == 0)) or (self.greats / total > 0.8): grade = "B"
            elif (self.greats / total > 0.6): grade = "C"
        elif self.mode == 2:
            if (self.accuracy == 1.0): grade = "SS"
            elif (self.accuracy > 0.98): grade = "S"
            elif (self.accuracy > 0.94): grade = "A"
            elif (self.accuracy > 0.90): grade = "B"
            elif (self.accuracy > 0.85): grade = "C"
        elif self.mode == 3:
            if (self.accuracy == 1.0): grade = "SS"
            elif (self.accuracy > 0.95): grade = "S"
            elif (self.accuracy > 0.90): grade = "A"
            elif (self.accuracy > 0.80): grade = "B"
            elif (self.accuracy > 0.70): grade = "C"
        if (grade in ["S", "SS"]) and (("HD" in self.mods) or ("FL" in self.mods) or ("FI" in self.mods)):
            grade += "H"
        return grade

    def get_mods(self, include_preference=False) -> str:
        mods = self.mods
        if not include_preference:
            mods = mods.replace('NC', 'DT')
            mods = mods.replace('SD', '')
            mods = mods.replace('PF', '')
            mods = mods.replace('MR', '')
        if mods.lower() in ['', 'nomod', 'none']:
            mods = "NM"
        return mods

    def search(self) -> str:
        return f"{self.user} +{self.mods} {self.accuracy:.2%} {self.grade}".lower()

    @classmethod
    def decode_database(cls, bytestream, database):
        # https://github.com/ppy/osu/wiki/Legacy-database-file-structure
        mode = StreamDecoder.byte(bytestream)
        bytestream.seek(4, 1)
        beatmap_hash = StreamDecoder.ulebstring(bytestream)
        beatmap = Beatmap.decode_beatmap_hash(beatmap_hash, database)
        user = StreamDecoder.ulebstring(bytestream)
        StreamDecoder.ulebsstring(bytestream)
        greats = StreamDecoder.short(bytestream)
        oks = StreamDecoder.short(bytestream)
        mehs = StreamDecoder.short(bytestream)
        perfects = StreamDecoder.short(bytestream)
        goods = StreamDecoder.short(bytestream)
        misses = StreamDecoder.short(bytestream)
        score = StreamDecoder.int(bytestream)
        combo = StreamDecoder.short(bytestream)
        perfect = StreamDecoder.bool(bytestream)
        mods = StreamDecoder.int(bytestream)
        StreamDecoder.sstring(bytestream)
        bytestream.seek(20, 1)
        if mods & 2 ** 23:
            bytestream.seek(8, 1)

        return cls(
            beatmap=beatmap,
            mode=mode,
            user=user,
            greats=greats,
            oks=oks,
            mehs=mehs,
            perfects=perfects,
            goods=goods,
            misses=misses,
            score=score,
            combo=combo,
            perfect=perfect,
            mods=Mod(mods).short_name(),
        )

    @classmethod
    def from_ossapi(cls, score, database):
        beatmap = Beatmap.from_ossapi(score, database)
        mode = score.mode_int
        greats = score.statistics.count_300
        oks = score.statistics.count_100
        mehs = score.statistics.count_50
        perfects = score.statistics.count_geki
        goods = score.statistics.count_katu
        misses = score.statistics.count_miss
        total_score = score.score
        combo = score.max_combo
        perfect = score.perfect
        mods = score.mods.short_name()

        return cls(
            beatmap=beatmap,
            mode=mode,
            greats=greats,
            oks=oks,
            mehs=mehs,
            perfects=perfects,
            goods=goods,
            misses=misses,
            score=total_score,
            combo=combo,
            perfect=perfect,
            mods=mods,
        )

    @classmethod
    def from_osustats(cls, score, database):
        beatmap = Beatmap.from_osustats(score, database)
        greats = score['count300']
        oks = score['count100']
        mehs = score['count50']
        perfects = score['countGeki']
        goods = score['countKatu']
        misses = score['countMiss']
        total_score = score['score']
        combo = score['maxCombo']
        perfect = bool(score['perfect'])
        mods = score['enabledMods'].replace(',', '')
        if 'NC' in mods:
            mods = mods.replace('DT', '')
        if 'PF' in mods:
            mods = mods.replace('SD', '')

        return cls(
            beatmap=beatmap,
            greats=greats,
            oks=oks,
            mehs=mehs,
            perfects=perfects,
            goods=goods,
            misses=misses,
            score=total_score,
            combo=combo,
            perfect=perfect,
            mods=mods,
        )
