import argparse
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from PIL import Image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Select region of the image and print its coordinates")
    parser.add_argument("source",
                        type=str,
                        help="image file")
    args = parser.parse_args()

    src = Image.open(args.source)

    plt.figure()
    plt.imshow(src)

    x0, x1, y0, y1 = 0, 0, 0, 0


    def onselect(eclick, erelease):
        global x0, x1, y0, y1
        x0 = int(eclick.xdata)
        y0 = int(eclick.ydata)
        x1 = int(erelease.xdata)
        y1 = int(erelease.ydata)
        print(f"{x0} {y0} {x1} {y1}")


    props = dict(facecolor=None, edgecolor="white", fill=False)
    rect = RectangleSelector(plt.gca(), onselect, interactive=False, props=props)

    plt.show()
