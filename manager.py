class Manager:

    def __init__(self):
        self.base_compare = set()
        self.new_compare = set()

    @property
    def difference(self):
        if not self.base_compare:
            return self.new_compare
        return self.new_compare - self.base_compare

    def add_comparison(self, comparison):
        self.base_compare.update(self.new_compare)
        self.new_compare = set(comparison)

    def to_reset(self):
        self.base_compare = set()
