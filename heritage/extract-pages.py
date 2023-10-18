import argparse
import fitz
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract pages from multiple PDF documents")
    parser.add_argument("--sources",
                        help="text file with the list of input files and page ranges",
                        type=str,
                        required=True)
    parser.add_argument("--destination",
                        help="output directory for extracted pages",
                        required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.destination):
        os.mkdir(args.destination)
    destination = os.path.abspath(args.destination)

    count = 0
    with open(args.sources, "r", encoding='utf-8') as f:
        for lines in f:
            info = lines.strip().split(",")
            if len(info) != 3:
                continue

            fn, start, end = info
            fn = fn.strip().replace("\"", "")

            p0 = int(start.strip()) - 1
            pn = int(end.strip()) - 1

            doc = fitz.Document(fn)
            for page_num in range(p0, pn):
                for img in doc.get_page_images(page_num):
                    xref = img[0]
                    image = doc.extract_image(xref)
                    pix = fitz.Pixmap(image["image"])
                    filename = os.path.join(destination, f"{count:04d}.png")
                    pix.save(filename)
                    count += 1




