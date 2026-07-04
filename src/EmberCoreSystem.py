class EmberCoreSystem:
    def __init__(self, ember_cores=0):
        self.ember_cores = ember_cores

    def increase_ember_cores(self, amount):
        if amount <= 0:
            return

        self.ember_cores += amount

    def get_ember_cores(self):
        return self.ember_cores

    def reduce_ember_cores(self, amount):
        if amount <= 0:
            return True

        if self.ember_cores < amount:
            return False

        self.ember_cores -= amount
        return True
