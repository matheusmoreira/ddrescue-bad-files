class File:
    def __init__(self, path, start, end):
        self.path = path
        self.start = start
        self.end = end
        self.size = end - start
        self.corrupt_blocks = []

    def total_corruption(self):
        total = 0

        for block in self.corrupt_blocks:
            start = self.start
            end = self.end

            if block.start > self.start:
                start = block.start
            if block.end < self.end:
                end = block.end

            total += end - start

        return total

    def corruption_percentage(self):
        if not self.corrupt_blocks:
            return 0
        else:
            return self.total_corruption() / self.size * 100

    def __str__(self):
        return "'{}' {} corrupt / {} bytes = {:.2f}%".format(
            self.path,
            self.corrupt,
            self.size,
            self.corruption_percentage()
        )

    def __repr__(self):
        return "<File '{}' @[{}, {}) = {} bytes, {} corrupt".format(
            self.path,
            self.start,
            self.end,
            self.size,
            self.corrupt
        )
