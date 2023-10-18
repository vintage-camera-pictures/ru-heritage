import argparse
import fitz
from PIL import Image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Append an image with the book cover to the converted PDF")
    parser.add_argument("--cover",
                        type=str,
                        help="cover image file",
                        required=True)
    parser.add_argument("--pdf",
                        type=str,
                        help="converted PDF file",
                        required=True)
    parser.add_argument("--destination",
                        type=str,
                        help="name of the destination PDF file",
                        required=True)
    parser.add_argument("--resolution",
                        help="(optional) resolution of the cover in DPI. Default is 100.",
                        type=float,
                        default=100.0)
    args = parser.parse_args()

    cover = Image.open(args.cover)
    cover.save(args.destination,
               "PDF",
               resolution=75.0)

    result = fitz.open()
    for pdf in (args.destination, args.pdf):
        with fitz.open(pdf) as f:
            result.insert_pdf(f)
    result.save(args.destination)
