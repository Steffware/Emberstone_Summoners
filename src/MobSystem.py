import random
from dataclasses import dataclass


STAT_EXPERIENCE_TO_LEVEL = 10
ADAPTABILITY_LEVEL_GAIN = 0.1

MOB_TYPES = [
    "Insect",
    "Canine",
    "Avian",
    "Serpent",
    "Arachnid",
    "Chameleon",
    "Ursine",
    "Turtle",
    "Owl",
    "Armadillo",
]

MOB_STATS = [
    "Vitality",
    "Ferocity",
    "Agility",
    "Intuition",
    "Precision",
    "Brutality",
    "Resilience",
    "Arcane",
    "Warding",
    "Adaptability",
]

STAT_DESCRIPTIONS = {
    "Vitality": "Livepoints",
    "Ferocity": "Critical hit chance",
    "Agility": "Ticks until attack",
    "Intuition": "Evade chance",
    "Precision": "Hit chance",
    "Brutality": "Hit damage",
    "Resilience": "Damage reduction",
    "Arcane": "Magic damage",
    "Warding": "Magic reduction",
    "Adaptability": "Exp. gain Multi.",
}


@dataclass
class Mob:
    name: str
    mob_type: str
    stats: dict
    stat_experience: dict
    rating: int = 1

    @property
    def sprite_key(self):
        return self.mob_type.lower() + "/" + self.name

    def get_stat_experience(self, stat_name):
        return self.stat_experience[stat_name]

    def get_stat_progress_percentage(self, stat_name):
        return self.get_stat_experience(stat_name) * 100 / STAT_EXPERIENCE_TO_LEVEL

    def stat_level_gain(self):
        return 2 ** (self.rating - 1)

    def add_stat_experience(self, stat_name, amount):
        gained_experience = amount * self.stats["Adaptability"]
        self.stat_experience[stat_name] += gained_experience

        while self.stat_experience[stat_name] >= STAT_EXPERIENCE_TO_LEVEL:
            self.stat_experience[stat_name] -= STAT_EXPERIENCE_TO_LEVEL
            stat_gain = self.stat_level_gain()
            if stat_name == "Adaptability":
                self.stats[stat_name] = round(
                    self.stats[stat_name] + (ADAPTABILITY_LEVEL_GAIN * stat_gain),
                    1,
                )
            else:
                self.stats[stat_name] += stat_gain

    def copy(self, rating=None):
        if rating is None:
            rating = self.rating

        return Mob(
            self.name,
            self.mob_type,
            {stat_name: stat_value * rating for stat_name, stat_value in self.stats.items()},
            self.stat_experience.copy(),
            rating,
        )


class MobSystem:
    def __init__(self):
        self.summon_pool = self.create_summon_pool()
        self.owned_mobs = []
        self.last_summoned_mob = None

    def get_owned_mobs(self):
        return self.owned_mobs

    def get_owned_mob(self, mob_index):
        return self.owned_mobs[mob_index]

    def remove_owned_mob(self, mob_index):
        mob = self.owned_mobs.pop(mob_index)
        if mob is self.last_summoned_mob:
            self.last_summoned_mob = None
        return mob

    def add_stat_experience(self, mob_index, stat_name, amount=1):
        self.get_owned_mob(mob_index).add_stat_experience(stat_name, amount)

    def summon_random_mob(self, rating=1):
        summoned_mob = random.choice(self.summon_pool).copy(rating)
        self.owned_mobs.append(summoned_mob)
        self.last_summoned_mob = summoned_mob
        return summoned_mob

    def get_last_summoned_mob(self):
        return self.last_summoned_mob

    @staticmethod
    def empty_stat_experience():
        return {stat_name: 0 for stat_name in MOB_STATS}

    @classmethod
    def create_summon_pool(cls):
        return [
            Mob(
                "Canis Placeholderus",
                "Canine",
                {
                    "Vitality": 5,
                    "Ferocity": 10,
                    "Agility": 5,
                    "Intuition": 5,
                    "Precision": 5,
                    "Brutality": 10,
                    "Resilience": 5,
                    "Arcane": 0,
                    "Warding": 0,
                    "Adaptability": 1.0,
                },
                cls.empty_stat_experience(),
            ),
            Mob(
                "Danger Noodle",
                "Serpent",
                {
                    "Vitality": 4,
                    "Ferocity": 5,
                    "Agility": 5,
                    "Intuition": 10,
                    "Precision": 5,
                    "Brutality": 5,
                    "Resilience": 3,
                    "Arcane": 4,
                    "Warding": 4,
                    "Adaptability": 1.0,
                },
                cls.empty_stat_experience(),
            ),
            Mob(
                "Skitterblob",
                "Arachnid",
                {
                    "Vitality": 2,
                    "Ferocity": 3,
                    "Agility": 7,
                    "Intuition": 5,
                    "Precision": 10,
                    "Brutality": 5,
                    "Resilience": 3,
                    "Arcane": 5,
                    "Warding": 5,
                    "Adaptability": 1.0,
                },
                cls.empty_stat_experience(),
            ),
        ]
