import argparse
import imageio.v3 as iio
import numpy as np
import os
from PIL import Image
import cv2


def parse(path):
    sizes = list()
    max_w, max_h = 0, 0
    for p, _, files in os.walk(path):
        for f in files:
            fn = os.path.join(p, f)
            info = iio.immeta(fn)
            w, h = info["shape"]
            max_w = max(max_w, w)
            max_h = max(max_h, h)
            sizes.append(fn)
    return sizes, (max_h, max_w)


def find_location(image, template_image, method=cv2.TM_CCOEFF_NORMED, threshold=0.45):
    res = cv2.matchTemplate(image, template_image, method)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val > threshold:
        return max_loc
    else:
        return None


def process_image(input_fn, max_size, border_ratio=0.0, border_value=255, template_image=None, remove_watermark=False):
    im = iio.imread(input_fn)
    new_shape = list(im.shape)
    if remove_watermark and template_image is not None:
        h, w = template_image.shape[:2]
        if len(im.shape) == 2:
            loc = find_location(im, template_image)
            if loc is not None:
                x, y = loc
                im[y:y + h, x:x + w] += 255 - template_image
            else:
                print(f"failed to remove watermark: '{input_fn}' (monochrome)")
        else:
            gray_scale = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            loc = find_location(gray_scale, template_image)
            if loc is not None:
                x, y = loc
                im[y:y + h, x:x + w, 0] += 255 - template_image
                im[y:y + h, x:x + w, 1] += 255 - template_image
                im[y:y + h, x:x + w, 2] += 255 - template_image
            else:
                print(f"failed to remove watermark: '{input_fn}' (colour)")

    new_shape[0] = max(new_shape[0], max_size[0])
    new_shape[1] = max(new_shape[1], max_size[1])
    b = int(border_ratio * new_shape[1])
    new_shape[0] += 2 * b
    new_shape[1] += 2 * b
    converted = border_value * np.ones(new_shape, dtype=im.dtype)
    x = (new_shape[0] - im.shape[0]) // 2
    y = (new_shape[1] - im.shape[1]) // 2
    if len(new_shape) == 3:
        converted[x:x + im.shape[0], y:y + im.shape[1], :] = im
    else:
        converted[x:x + im.shape[0], y:y + im.shape[1]] = im

    return converted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-process images downloaded from e-heritage.ru")
    parser.add_argument("--input",
                        help="Directory containing downloaded images",
                        type=str,
                        required=True)
    parser.add_argument("--output",
                        help="Output directory",
                        type=str,
                        required=True)
    parser.add_argument("--border", "-b",
                        help="Add borders defined by a fraction of the image width. Default is 0.",
                        type=float,
                        default=0.0,
                        required=False)
    parser.add_argument("--skip", "-s",
                        help="Skip start pages",
                        type=int,
                        default=0,
                        required=False)
    parser.add_argument("--remove-watermark",
                        help="remove watermark",
                        action="store_true")
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f'Unable to find input directory "{args.input}"')
        exit(1)

    template = None
    if args.remove_watermark:
        template = cv2.imread("./data/template.png", cv2.IMREAD_GRAYSCALE)

    filenames, m = parse(args.input)
    if len(filenames) > 0:
        c = process_image(input_fn=filenames[args.skip],
                          max_size=m,
                          border_ratio=args.border,
                          border_value=255,
                          template_image=template,
                          remove_watermark=args.remove_watermark)
        pdf = Image.fromarray(c)
        rest = (Image.fromarray(process_image(input_fn=f,
                                              max_size=m,
                                              border_ratio=args.border,
                                              border_value=255,
                                              template_image=template,
                                              remove_watermark=args.remove_watermark)) for f in
                filenames[args.skip + 1:])

        pdf.save(args.output,
                 "PDF",
                 resolution=100.0,
                 save_all=True,
                 append_images=rest)
