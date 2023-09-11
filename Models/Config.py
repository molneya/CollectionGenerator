
from dataclasses import dataclass
from configparser import ConfigParser
from time import time
import shutil
import os

@dataclass
class Config:
    directory: str=None
    app_id: int=0
    app_token: str=None
    bests: str="{0}'s {1} bests"
    single: str="{0}'s {1} #{2}s"
    range: str="{0}'s {1} #{2}-#{3}s"
    modded: str="+{0}"
    duplicate: str="{0} (Duplicate)"
    inverse: str="{0} (Inverse)"
    subtract: str="{0} (Subtract {1})"
    merged: str="(Merged {0})"
    intersect: str="(Intersect {0})"
    leeways: str="{0:.1f}~{1:.1f} +{2}"

    @staticmethod
    def dirpath():
        appdata = os.getenv("appdata")
        dir = os.path.join(appdata, "CollectionGenerator")
        path = os.path.join(dir, "config.ini")
        return dir, path

    @staticmethod
    def makepath(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def backup(source):
        # Don't make a backup if we aren't overwriting anything
        if not os.path.exists(source):
            return
        dir, _ = Config.dirpath()
        backup_dir = os.path.join(dir, "backups")
        Config.makepath(dir)
        Config.makepath(backup_dir)
        timestamp = int(time())
        basename = os.path.basename(source)
        dest = os.path.join(backup_dir, f"{timestamp}-{basename}")
        shutil.copyfile(source, dest)

    def load(self):
        dir, path = self.dirpath()
        # Load from path directly if it exists
        if os.path.exists(path):
            self.read(path)
            return
        # Otherwise, make config for next time
        self.makepath(dir)
        self.write(path)

    def save(self):
        dir, path = self.dirpath()
        self.makepath(dir)
        self.write(path)

    def read(self, path):
        config = ConfigParser()
        config.read(path, encoding="utf-8-sig")
        self.directory = config.get("Main", "directory", fallback=Config.directory)
        self.app_id = config.getint("API", "app_id", fallback=Config.app_id)
        self.app_token = config.get("API", "app_token", fallback=Config.app_token)
        self.bests = config.get("Collections", "bests", fallback=Config.bests)
        self.single = config.get("Collections", "single", fallback=Config.single)
        self.range = config.get("Collections", "range", fallback=Config.range)
        self.modded = config.get("Collections", "modded", fallback=Config.modded)
        self.duplicate = config.get("Collections", "duplicate", fallback=Config.duplicate)
        self.inverse = config.get("Collections", "inverse", fallback=Config.inverse)
        self.subtract = config.get("Collections", "subtract", fallback=Config.subtract)
        self.merged = config.get("Collections", "merged", fallback=Config.merged)
        self.intersect = config.get("Collections", "intersect", fallback=Config.intersect)
        self.leeways = config.get("Collections", "leeways", fallback=Config.leeways)

    def write(self, path):
        config = ConfigParser()
        config.add_section("Main")
        config.add_section("API")
        config.add_section("Collections")
        config.set("Main", "directory", self.directory or "")
        config.set("API", "app_id", str(self.app_id))
        config.set("API", "app_token", self.app_token or "")
        config.set("Collections", "bests", self.bests)
        config.set("Collections", "single", self.single)
        config.set("Collections", "range", self.range)
        config.set("Collections", "modded", self.modded)
        config.set("Collections", "duplicate", self.duplicate)
        config.set("Collections", "inverse", self.inverse)
        config.set("Collections", "subtract", self.subtract)
        config.set("Collections", "merged", self.merged)
        config.set("Collections", "intersect", self.intersect)
        config.set("Collections", "leeways", self.leeways)
        with open(path, 'w', encoding="utf-8-sig") as f:
            config.write(f)
