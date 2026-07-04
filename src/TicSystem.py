class TicSystem:
    def __init__(self, tics_per_second):
        if tics_per_second <= 0:
            raise ValueError("tics_per_second must be greater than zero")

        self.tics_per_second = tics_per_second
        self.seconds_per_tic = 1 / tics_per_second
        self.current_tic = 0
        self.accumulator = 0

    def update(self, dt):
        self.accumulator += dt
        tics_elapsed = 0

        while self.accumulator >= self.seconds_per_tic:
            self.accumulator -= self.seconds_per_tic
            self.current_tic += 1
            tics_elapsed += 1

        return tics_elapsed

    def get_current_tic(self):
        return self.current_tic
