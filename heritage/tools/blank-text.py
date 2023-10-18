import argparse
from PIL import Image
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blank part of page using a background image")
    parser.add_argument("--source",
                        help="source image",
                        type=str,
                        required=True)
    parser.add_argument("--region",
                        help="source region to be blanked in pixel coordinates: top left bottom right",
                        type=int,
                        nargs="+",
                        required=True),
    parser.add_argument("--background",
                        help="background image",
                        type=str,
                        required=True)
    parser.add_argument("--border",
                        help="border width in pixels",
                        type=int,
                        default=0,
                        required=False)
    parser.add_argument("--destination",
                        help="destination for the blanked image",
                        type=str,
                        required=True)
    args = parser.parse_args()

    src = Image.open(args.source)
    x0, y0, x1, y1 = args.region
    background = Image.open(args.background)
    b = args.border
    box = (x0, y0, x1, y1)
    patch = background.crop(box)
    mean_patch = np.mean(patch)

    src_data = np.array(src)
    b = args.border
    margin_left = src.crop((b, y0-1, x0-1, y1-1))
    w, h = src.size
    margin_right = src.crop((x1, y0-1, w-b, y1-1))
    mean_margin = 0.5 * np.mean(margin_left) + 0.5 * np.mean(margin_right)

    adjusted = np.array(patch, dtype=float) + mean_margin - mean_patch
    patch = Image.fromarray(adjusted.astype(np.uint8))

    src.paste(patch, box[:2])
    src.save(args.destination)

