from data import Header, Pixel, Image, MalformedPixelError,\
        PartialPixelError, P3InvalidHeaderError
import sys
from typing import Any, List, TextIO, Tuple

MALFORMED_PIXEL = "invalid pixel at <row={}, col={}>"
PARTIAL_PIXEL = "partial pixel at <row={}, col={}>"

P3_ID = 'P3'


# Convert a value to an integer. If this fails, return a default value.
# input: value as Any
# input: default as int
# result: converted value or default
def _convert_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except ValueError:
        return default


# Convert the dimensions for the ppm P3 format to integers.
# input: dimensions as a string
# result: pair of integer values representing width and height
def _convert_dimensions(dimension_str: str) -> Tuple[int, int]:
    dim_list = dimension_str.split()
    if len(dim_list) == 2:
        width = _convert_int(dim_list[0], None)
        height = _convert_int(dim_list[1], None)

        if width is not None and height is not None:
            return (width, height)

    raise P3InvalidHeaderError()


# Convert the maximum color for the ppm P3 format to an integer.
# input: color as string
# result: integer value
def _convert_color(color_str: str) -> int:
    max_color = _convert_int(color_str, None)

    if max_color is None:
        raise P3InvalidHeaderError()

    return max_color


# Read (and return) the P3 header from the provided input stream.
# input: input file as TextIO
# result: Header
def _read_header(infile: TextIO) -> Header:
    first = infile.readline().strip()
    second = infile.readline().strip()
    third = infile.readline().strip()
    if first != P3_ID or second == '' or third == '':
        raise P3InvalidHeaderError()

    (width, height) = _convert_dimensions(second)
    max_color = _convert_color(third)

    return Header(width, height, max_color)


# Convert list of strings into a proper pixel or report an error.
# input: values as list of strings
# input: row as int, for error messages
# input: col as int, for error messages
# result: newly converted pixel
def _create_pixel(values: List[str], row: int, col: int) -> Pixel:
    if len(values) < 3:
        raise PartialPixelError(PARTIAL_PIXEL.format(row, col))

    red = _convert_int(values[0], None)
    green = _convert_int(values[1], None)
    blue = _convert_int(values[2], None)

    if red is None or green is None or blue is None:
        raise MalformedPixelError(MALFORMED_PIXEL.format(row, col))

    return Pixel(red, green, blue)


# Group elements of a list into sublists of size 3.
# input: values as string list
# result: list of string lists
def _groups_of_3(values: List[str]) -> List[List[str]]:
    return [values[i:i + 3] for i in range(0, len(values), 3)]


# Read the contents of a P3 ppm file.
# input: input file as TextIO
# result: Image with header and pixels
def get_image(infile: TextIO) -> Image:
    header = _read_header(infile)
    contents = ''.join(infile.readlines()).split()
    pixels = [_create_pixel(group, idx // header.width, idx % header.width)
              for idx, group in enumerate(_groups_of_3(contents))]
    return Image(header, pixels)

