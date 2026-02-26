from typing import List

class Header:
    def __init__(self, width: int, height: int, max_color: int):
        self.width = width
        self.height = height
        self.max_color = max_color

    def __eq__(self, other: object) -> bool:
        return (type(other) is Header
                and self.width == other.width
                and self.height == other.height
                and self.max_color == other.max_color)


class Pixel:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue

    def __eq__(self, other: object) -> bool:
        return (type(other) is Pixel
                and self.red == other.red
                and self.green == other.green
                and self.blue == other.blue)

    def __str__(self) -> str:
        return '{} {} {}'.format(self.red, self.green, self.blue)


class Image:
    def __init__(self, header: Header, pixels: List[Pixel]):
        self.header = header
        self.pixels = pixels


class MalformedPixelError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PartialPixelError(Exception):
    def __init__(self, message):
        super().__init__(message)


class P3InvalidHeaderError(Exception):
    pass

