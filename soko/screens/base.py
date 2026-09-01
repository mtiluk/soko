import displayio

class Screen:
    def __init__(self):
        self.group = displayio.Group()
        self.group.hidden = True
        self.build()

    def build(self):
        """Create display objects once."""

    def enter(self):
        """Reset animation clocks when shown."""

    def tick(self, dt):
        """Called every frame while visible."""
