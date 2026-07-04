import math
import random
from dataclasses import dataclass, field


STAT_BASE_EXPERIENCE_TO_LEVEL = 10
STAT_EXPERIENCE_COST_MULTIPLIER = 1.1
ADAPTABILITY_LEVEL_GAIN = 0.1

POTENTIAL_MULTIPLIERS = {
    "Incompetent": 0.8,
    "Poor": 0.9,
    "Normal": 1.0,
    "Good": 1.1,
    "Exceptional": 1.2,
}
POTENTIAL_LEVELS = list(POTENTIAL_MULTIPLIERS.keys())

MOB_TYPES = [
    "Insect",
    "Insectoid",
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
    potential: str = "Normal"
    stat_levels: dict = field(default_factory=dict)

    def __post_init__(self):
        for stat_name in MOB_STATS:
            self.stat_experience.setdefault(stat_name, 0)
            self.stat_levels.setdefault(stat_name, 0)
        if self.potential not in POTENTIAL_MULTIPLIERS:
            self.potential = "Normal"

    @property
    def sprite_key(self):
        return self.mob_type.lower() + "/" + self.name

    def get_stat_experience(self, stat_name):
        return self.stat_experience[stat_name]

    def get_stat_experience_to_level(self, stat_name):
        return self.stat_experience_to_level(self.stat_levels[stat_name])

    @staticmethod
    def stat_experience_to_level(stat_level):
        experience_to_level = STAT_BASE_EXPERIENCE_TO_LEVEL
        for _ in range(stat_level):
            experience_to_level = math.ceil(experience_to_level * STAT_EXPERIENCE_COST_MULTIPLIER)
        return experience_to_level

    def get_stat_progress_percentage(self, stat_name):
        return self.get_stat_experience(stat_name) * 100 / self.get_stat_experience_to_level(stat_name)

    def potential_multiplier(self):
        return POTENTIAL_MULTIPLIERS[self.potential]

    def stat_level_gain(self):
        return math.ceil((2 ** (self.rating - 1)) * self.potential_multiplier())

    def add_stat_experience(self, stat_name, amount):
        gained_experience = amount * self.stats["Adaptability"]
        self.stat_experience[stat_name] += gained_experience

        while self.stat_experience[stat_name] >= self.get_stat_experience_to_level(stat_name):
            self.stat_experience[stat_name] -= self.get_stat_experience_to_level(stat_name)
            self.stat_levels[stat_name] += 1
            stat_gain = self.stat_level_gain()
            if stat_name == "Adaptability":
                self.stats[stat_name] = round(
                    self.stats[stat_name] + (ADAPTABILITY_LEVEL_GAIN * stat_gain),
                    1,
                )
            else:
                self.stats[stat_name] += stat_gain

    def copy(self, rating=None, potential=None):
        if rating is None:
            rating = self.rating
        if potential is None:
            potential = self.potential

        return Mob(
            self.name,
            self.mob_type,
            self.scaled_spawn_stats(self.stats, rating, potential),
            self.stat_experience.copy(),
            rating,
            potential,
            self.stat_levels.copy(),
        )

    @staticmethod
    def scaled_spawn_stats(stats, rating, potential):
        potential_multiplier = POTENTIAL_MULTIPLIERS.get(potential, POTENTIAL_MULTIPLIERS["Normal"])
        scaled_stats = {}
        for stat_name, stat_value in stats.items():
            scaled_value = stat_value * rating * potential_multiplier
            if stat_name == "Adaptability":
                scaled_stats[stat_name] = round(scaled_value, 1)
            else:
                scaled_stats[stat_name] = math.ceil(scaled_value)
        return scaled_stats


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

    def random_potential(self):
        return random.choice(POTENTIAL_LEVELS)

    def add_owned_mob(self, mob):
        self.owned_mobs.append(mob)
        self.last_summoned_mob = mob
        return mob

    def summon_random_mob(self, rating=1):
        summoned_mob = random.choice(self.summon_pool).copy(rating, self.random_potential())
        return self.add_owned_mob(summoned_mob)

    def get_last_summoned_mob(self):
        return self.last_summoned_mob

    @staticmethod
    def empty_stat_experience():
        return {stat_name: 0 for stat_name in MOB_STATS}

    @staticmethod
    def balanced_stats():
        return {
            stat_name: 1.0 if stat_name == "Adaptability" else 5
            for stat_name in MOB_STATS
        }

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
            Mob(
                "Belt Buddy",
                "Armadillo",
                cls.balanced_stats(),
                cls.empty_stat_experience(),
            ),
            Mob(
                "Birb",
                "Avian",
                cls.balanced_stats(),
                cls.empty_stat_experience(),
            ),
            Mob(
                "Common Green Boy",
                "Chameleon",
                cls.balanced_stats(),
                cls.empty_stat_experience(),
            ),
            Mob(
                "Creepy Crawler",
                "Insectoid",
                cls.balanced_stats(),
                cls.empty_stat_experience(),
            ),
            Mob(
                "Fluffy Friend",
                "Ursine",
                cls.balanced_stats(),
                cls.empty_stat_experience(),
            ),
            Mob(
                "Professor Hoot",
                "Owl",
                cls.balanced_stats(),
                cls.empty_stat_experience(),
            ),
            Mob(
                "Shelly",
                "Turtle",
                cls.balanced_stats(),
                cls.empty_stat_experience(),
            ),
        ]
