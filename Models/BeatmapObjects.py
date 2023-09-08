
from ctypes import c_float

class Spinner:
    def __init__(self, x, y, time, end_time):
        self.x = x
        self.y = y
        self.time = time
        self.duration = end_time - time

    def rotations(self, rate):
        max_speed = c_float(0)
        rotations = c_float(0)
        inertia = (0.00008 + max(0, 5000 - self.duration) / 1000 / 2000) / rate
        ticks = self.duration - int(rate * 50 / 3)
        for _ in range(ticks):
            max_speed = c_float(max_speed.value + inertia)
            rotations = c_float(rotations.value + min(max_speed.value, 0.05) * 0.318309886184)
        return rotations.value

    def requirement(self, od):
        num = 3 + 0.4 * od if od <= 5.0 else 2.5 + 0.5 * od
        return int(num * self.duration / 1000)

    def leeway(self, rate, od):
        rotations = self.rotations(rate)
        requirement = self.requirement(od)
        return self._leeway(rotations, requirement)

    def _bonus(self, rotations, requirement):
        bonus = max(0, int(rotations) - (requirement + 3))
        return (bonus // 2) * 1000

    def _final_hundred(self, rotations, requirement):
        bonus = max(0, int(rotations) - (requirement + 3))
        if (requirement % 2 != 0):
            return False
        return not bonus % 2 == 0

    def _bonus_hundred(self, rotations, requirement):
        return not requirement % 2

    def _leeway(self, rotations, requirement):
        if requirement % 2 and int(rotations) % 2:
            return rotations - int(rotations) + 1
        return rotations - int(rotations)

    @classmethod
    def parse(cls, data):
        params = data.split(',')
        type = int(float(params[3]))
        if not type & 8:
            return
        x = int(float(params[0]))
        y = int(float(params[1]))
        time = int(float(params[2]))
        end_time = int(float(params[5]))
        return cls(x, y, time, end_time)
