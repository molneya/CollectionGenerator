
from Models.BeatmapObjects import Spinner

class BeatmapParser:
    def __init__(self, hit_objects, overall_difficulty):
        self.hit_objects = hit_objects
        self.overall_difficulty = overall_difficulty

    def get_leeways(self, mods):
        rate = 1.0
        od = self.overall_difficulty
        if 'DT' in mods:
            rate = 1.5
        if 'EZ' in mods:
            od *= 0.5
        if 'HT' in mods:
            rate = 0.75
        if 'HR' in mods:
            od = min(od * 1.4, 10)
        return [spinner.leeway(rate, od) for spinner in self.hit_objects]

    @classmethod
    def from_file(cls, filename):
        try:
            with open(filename, 'r', encoding="utf-8-sig") as f:
                data = f.read()
            return cls.parse(data)
        # A multitude of reasons why this could fail. Incorrect encoding, missing files, corrupted files, you name it.
        # Leave this for future me to figure out.
        except:
            return cls([], 0)

    @classmethod
    def parse(cls, data):
        hit_objects = []
        current_section = None

        for line in data.splitlines():
            line = line.strip()

            # Ignore lines with no content or are comments
            if not line or line.startswith('//'):
                continue

            # Extract section name
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                continue

            # Parse Difficulty
            elif current_section == "Difficulty":
                key, value = line.split(':', 1)
                if key == "OverallDifficulty":
                    overall_difficulty = float(value)

            # Parse HitObjects
            elif current_section == "HitObjects":
                object = Spinner.parse(line)
                if object:
                    hit_objects.append(object)

        return cls(hit_objects, overall_difficulty)
