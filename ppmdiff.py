from data import Header, Pixel, Image, MalformedPixelError,\
        PartialPixelError, P3InvalidHeaderError
import sys
from typing import List, TextIO
import utility

OUT_FILE_DIGITAL = 'diffimage_digital.ppm'
OUT_FILE_ANALOG = 'diffimage_analog.ppm'

NUM_ARGS = 3
FILE_ARG1 = 1
FILE_ARG2 = 2

PROG_NAME = 'ppmdiff.py'

COLUMN_MISMATCH = 'widths differ'
ROW_MISMATCH = 'heights differ'
MAX_COLOR_MISMATCH = 'color max values differ'
NO_MISMATCH = 'nothing differs'
INVALID_P3_FORMAT = 'invalid P3 header format'
HEADER_MISMATCH = 'Headers mismatch: {}'


# Check the command-line arguments for basic validity.
# input: arguments as string list
# result: boolean value indicating basic validity
def check_args(argv: List[str]) -> bool:
    return len(argv) == NUM_ARGS


# Determine the program name, or use a default value.
# input: arguments as string list
# result: program name from list or default value
def prog_name(argv: List[str]) -> str:
    if argv and argv[0]:
        return argv[0]
    else:
        return PROG_NAME


# Print an error message and exit.
# input: error message as a string
def error(msg: str) -> None:
    print('{}'.format(msg), file=sys.stderr)
    sys.exit(1)


# Print a usage error message.
# input: program name as string
def usage(name: str) -> None:
    error('usage: {} image1.ppm image2.ppm'.format(name))


# Attempt to open a file, reporting an error as appropriate.
# input: file name/path as a string
# input: read/write mode
# result: opened file as TextIO
def open_file(name: str, mode: str) -> TextIO:
    try:
        return open(name, mode)
    except IOError as e:
        error('{0}: {1}'.format(name, e.strerror))


# Print the header to an output stream.
# input: output stream
# input: header as Header
def write_header(out: TextIO, h: Header) -> None:
    print('P3\n', file=out)
    print('{} {}\n'.format(h.width, h.height), file=out)
    print('{}\n'.format(h.max_color), file=out)


# Determine the component difference between two pixels.
# input: p1 as Pixel
# input: p2 as Pixel
# result: difference as Pixel
def pixel_diff(p1: Pixel, p2: Pixel) -> Pixel:
    return Pixel(abs(p1.red - p2.red), abs(p1.green - p2.green),
                 abs(p1.blue - p2.blue))


# Determine the reason for a header mismatch.
# input: h1 as Header
# input: h2 as Header
# result: mismatch message
def header_match_error(h1: Header, h2: Header) -> str:
    if h1.width != h2.width:
        return COLUMN_MISMATCH
    elif h1.height != h2.height:
        return ROW_MISMATCH
    elif h1.max_color != h2.max_color:
        return MAX_COLOR_MISMATCH
    else:
        return NO_MISMATCH


# Process pixels in two images to determine differences. Print differences
# to output streams.
# input: pixels1 as Pixel list
# input: pixels2 as Pixel list
# input: digital output stream
# input: analog output stream
# input: header as Header
# result: boolean indicating mismatch found
def process_pixels(pixels1: List[Pixel], pixels2: List[Pixel],
        out_digital: TextIO, out_analog: TextIO, header: Header) -> bool:
    differ = False

    for (idx, (pixel1, pixel2)) in enumerate(zip(pixels1, pixels2)):
        if pixel1 == pixel2:
            print('{} {} {} '.format(header.max_color, header.max_color,
                                     header.max_color), file=out_analog)
            print('{} {} {} '.format(header.max_color, header.max_color,
                                     header.max_color), file=out_digital)
        else:
            diff = pixel_diff(pixel1, pixel2)
            print('pixels at <row={}, col={}> differ.  '.format(
                idx // header.width, idx % header.width),
                file=sys.stderr, end='')
            print('{} <-- --> {}'.format(pixel1, pixel2), file=sys.stderr)
            print('{} {} {} '.format(header.max_color - diff.red,
                                     header.max_color - diff.green, header.max_color - diff.blue),
                  file=out_analog)
            print('0 0 0 '.format(), file=out_digital)
            differ = True

    return differ


# Generate the difference images.
# input: pixels1 as Pixel list
# input: pixels2 as Pixel list
# input: digital output stream
# input: analog output stream
# input: header as Header
# result: boolean indicating mismatch found
def generate_diffs(pixels1: List[Pixel], pixels2: List[Pixel],
        out_digital: TextIO, out_analog: TextIO, header: Header) -> bool:
    write_header(out_digital, header)
    write_header(out_analog, header)
    return process_pixels(pixels1, pixels2, out_digital, out_analog, header)


# Process the P3 image files in the argument list to create difference images.
# input: argument list as string list
def main(argv: List[str]) -> None:
    try:
        if check_args(argv):
            with (open_file(argv[FILE_ARG1], 'r') as infile1,
                    open_file(argv[FILE_ARG2], 'r') as infile2):
                image1 = utility.get_image(infile1)
                image2 = utility.get_image(infile2)

            if image1.header != image2.header:
                error(HEADER_MISMATCH.format(
                        header_match_error(image1.header, image2.header)))

            with (open_file(OUT_FILE_DIGITAL, 'w') as out_digital,
                    open_file(OUT_FILE_ANALOG, 'w') as out_analog):

                diff = generate_diffs(image1.pixels, image2.pixels,
                        out_digital, out_analog, image1.header)
            sys.exit(diff)
        else:
            usage(prog_name(argv))
    except utility.MalformedPixelError as err:
        error(err)
    except utility.P3InvalidHeaderError:
        error(INVALID_P3_FORMAT)
    except utility.PartialPixelError as err:
        error(err)


if __name__ == '__main__':
    main(sys.argv)
