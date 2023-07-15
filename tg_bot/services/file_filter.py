import re


def file_filter(path: str):
    sorted_lst = set()
    with open(path, encoding="utf-8") as f:
        lst = f.readlines()
        for line in lst:
            line = line.replace("✅", "").strip()
            line = re.sub(r"([\s\S]*?)(<[^>]*>)", r"\1", line)
            if not line:
                continue
            # line = line.replace("\"", "«", 1).replace("\"", "»", 1)
            sorted_lst.add(line.capitalize())

    with open(path, encoding="utf-8", mode="w+") as f:
        f.write("\n".join(sorted(sorted_lst)))


# if __name__ == '__main__':
#     file_filter("../../systemd/decks/1.txt")
