import argparse
import urllib3
import random
import time
import os

BOOK_ID = "10075280"
BASE_URL = "http://e-heritage.ru"
URL = f"{BASE_URL}/Book"
PAUSE_LOWER = 1
PAUSE_UPPER = 10

http = urllib3.PoolManager()


def get_variables(url):
    resp = http.request("GET", url)
    if resp.status != 200:
        raise RuntimeError(f'GET "{url}" failed with status {resp.status}')

    html = resp.data.decode("utf-8")
    variables = dict()
    lines = html.split("\r\n")
    for k in range(len(lines)):
        if lines[k].strip() != '<script type="text/javascript">':
            continue
        k += 1
        while lines[k].strip() != "</script>":
            line = lines[k]
            k += 1
            line = line.replace("var", "")
            line = line.replace(";", "").strip()
            n, v = line.split("=")
            if v.startswith("'"):
                v = v.replace("'", "")
                variables[n.strip()] = v.strip()
            else:
                variables[n.strip()] = int(v.strip())
    return variables


def get_image_src(data):
    if "src=" not in data:
        print(f'response "{data}" does not contain image source field')
        exit(2)
    _, u = data.split("src=")
    parts = u.split("\"")
    if len(parts) != 3:
        print(f'wrong format of image: "{data}"')
        exit(3)
    return parts[1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download books from e-heritage.ru")
    parser.add_argument("--book-id",
                        help="book ID in the e-heritage.ru system",
                        type=str,
                        default=BOOK_ID,
                        required=False)
    parser.add_argument("--output",
                        help="output directory",
                        type=str,
                        default=os.getcwd(),
                        required=False)
    args = parser.parse_args()
    if not os.path.isdir(args.output):
        print(f'output directory "{args.output}" does not exist')
        exit(1)

    info = get_variables(url=f"{URL}/{args.book_id}")
    start_page = info["curImage"]
    end_page = info["lastImage"]
    for page in range(start_page, end_page + 1):
        fields = {"sesid": info["session"],
                  "page": page,
                  "zoom": info["maxZoom"],
                  "turn": 0}
        uri = f"{URL}/GetImageDiv"
        r = http.request("POST",
                         uri,
                         fields=fields
                         )
        if r.status != 200:
            print(f'POST request to "{uri}" with parameters {fields} failed with status {r.status}')
            exit(1)

        content = r.data.decode("utf-8")
        image_url = get_image_src(content)

        uri = f"{BASE_URL}{image_url}"
        r = http.request("GET", uri)
        if r.status != 200:
            print(f'GET request to "{uri}" failed with status {r.status}')
            exit(4)

        fn = os.path.join(args.output, f"page_{page:06d}.png")
        with open(fn, "wb") as fo:
            fo.write(r.data)
        pause = random.randint(PAUSE_LOWER, PAUSE_UPPER)
        time.sleep(pause)

