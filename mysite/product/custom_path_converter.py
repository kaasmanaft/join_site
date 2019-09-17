

class SimaSlug:
    regex = r'[-_\w/]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
