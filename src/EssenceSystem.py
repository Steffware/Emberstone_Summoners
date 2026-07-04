import math


class EssenceSystem:
    def __init__(self, essence=0, essence_rate=0.1):
        self.essence = essence
        self.essence_rate = essence_rate

    def update_tics(self, tics_elapsed, tics_per_second):
        if tics_elapsed <= 0:
            return

        self.essence += (self.essence_rate / tics_per_second) * tics_elapsed

    def multiply_essence_rate(self, multiplier):
        if multiplier <= 0:
            return

        self.essence_rate *= multiplier

    def increase_essence(self, amount):
        if amount <= 0:
            return

        self.essence += amount

    def has_essence(self, amount):
        return self.essence >= amount

    def reduce_essence(self, amount):
        if amount < 0 or not self.has_essence(amount):
            return False

        self.essence -= amount
        return True

    def get_essence_text(self):
        return "Essence: " + self.format_number(self.essence)

    def get_rate_text(self):
        return "Rate: " + self.format_number(self.essence_rate) + "/s"

    @staticmethod
    def format_number(value):
        if abs(value) >= 1000:
            exponent = int(math.floor(math.log10(abs(value))))
            mantissa = value / (10 ** exponent)

            if abs(mantissa) >= 10:
                mantissa /= 10
                exponent += 1

            formatted_mantissa = f"{mantissa:.3f}".rstrip("0").rstrip(".")
            return formatted_mantissa + "e" + str(exponent)

        formatted = f"{value:.2f}".rstrip("0").rstrip(".")
        if formatted == "-0":
            return "0"
        return formatted
