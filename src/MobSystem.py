import math
import random
from dataclasses import dataclass


POWER_BASE = 100
POWER_BASE_EXPERIENCE_TO_LEVEL = 10
POWER_EXPERIENCE_COST_MULTIPLIER = 1.1
SPIRIT_BASE_LEVEL = 1
SPIRIT_BASE_MULTIPLIER = 1

POTENTIAL_MULTIPLIERS = {
    "Incompetent": 0.8,
    "Poor": 0.9,
    "Normal": 1.0,
    "Good": 1.1,
    "Exceptional": 1.2,
}
POTENTIAL_LEVELS = list(POTENTIAL_MULTIPLIERS.keys())

SPIRIT_MULTIPLIER_GAINS = {
    "Mundane": 0.01,
    "Enchanted": 0.03,
    "Arcane": 0.05,
    "Mystic": 1.1,
}
SPIRIT_TYPES = list(SPIRIT_MULTIPLIER_GAINS.keys())

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


@dataclass
class Mob:
    name: str
    mob_type: str
    rating: int = 1
    potential: str = "Normal"
    base_power: int = POWER_BASE
    power_experience: float = 0
    power_level: int = 0
    spirit_type: str = "Mundane"
    spirit_multiplier: float = SPIRIT_BASE_MULTIPLIER
    spirit_experience: float = 0
    spirit_level: int = SPIRIT_BASE_LEVEL

    def __post_init__(self):
        if self.potential not in POTENTIAL_MULTIPLIERS:
            self.potential = "Normal"
        if self.spirit_type not in SPIRIT_MULTIPLIER_GAINS:
            self.spirit_type = "Mundane"

    @property
    def sprite_key(self):
        return self.mob_type.lower() + "/" + self.name

    def potential_multiplier(self):
        return POTENTIAL_MULTIPLIERS[self.potential]

    @property
    def power(self):
        return math.ceil(round(self.base_power + sum(self.power_multiplier_bonuses()), 10))

    def power_multiplier_bonuses(self):
        return [
            self.base_power * (self.potential_multiplier() - 1),
            self.base_power * (self.spirit_multiplier - 1),
        ]

    def get_power_experience(self):
        return self.power_experience

    def get_power_experience_to_level(self):
        return self.power_experience_to_level(self.power_level)

    @staticmethod
    def power_experience_to_level(power_level):
        experience_to_level = POWER_BASE_EXPERIENCE_TO_LEVEL
        for _ in range(power_level):
            experience_to_level = math.ceil(experience_to_level * POWER_EXPERIENCE_COST_MULTIPLIER)
        return experience_to_level

    def get_power_progress_percentage(self):
        return self.power_experience * 100 / self.get_power_experience_to_level()

    def add_power_experience(self, amount):
        self.power_experience += amount

        while self.power_experience >= self.get_power_experience_to_level():
            self.power_experience -= self.get_power_experience_to_level()
            self.power_level += 1
            self.base_power += self.power_level_gain()

    def power_level_gain(self):
        return self.rating

    def get_spirit_experience(self):
        return self.spirit_experience

    def get_spirit_experience_to_level(self):
        return self.spirit_level

    def get_spirit_progress_percentage(self):
        return self.spirit_experience * 100 / self.get_spirit_experience_to_level()

    def add_spirit_experience(self, amount):
        self.spirit_experience += amount

        while self.spirit_experience >= self.get_spirit_experience_to_level():
            self.spirit_experience -= self.get_spirit_experience_to_level()
            self.spirit_level += 1
            self.spirit_multiplier = round(
                self.spirit_multiplier + SPIRIT_MULTIPLIER_GAINS[self.spirit_type],
                2,
            )

    def copy(self, rating=None, potential=None):
        if rating is None:
            rating = self.rating
        if potential is None:
            potential = self.potential

        return Mob(self.name, self.mob_type, rating, potential)


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

    def add_power_experience(self, mob_index, amount=1):
        self.get_owned_mob(mob_index).add_power_experience(amount)

    def add_spirit_experience(self, mob_index, amount=1):
        self.get_owned_mob(mob_index).add_spirit_experience(amount)

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

    @classmethod
    def create_summon_pool(cls):
        return [
            Mob("Canis Placeholderus", "Canine"),
            Mob("Danger Noodle", "Serpent"),
            Mob("Skitterblob", "Arachnid"),
            Mob("Belt Buddy", "Armadillo"),
            Mob("Birb", "Avian"),
            Mob("Common Green Boy", "Chameleon"),
            Mob("Creepy Crawler", "Insectoid"),
            Mob("Fluffy Friend", "Ursine"),
            Mob("Professor Hoot", "Owl"),
            Mob("Shelly", "Turtle"),
        ]
