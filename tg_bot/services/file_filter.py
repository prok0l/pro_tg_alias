import re


def word_filter(line: str) -> str:
    line = line.replace("✅", "").strip()
    line = re.sub(r"([\s\S]*?)(<[^>]*>)", r"\1", line)
    line = line.replace("<", "").replace(">", "")
    return line


def file_filter(path: str):
    sorted_lst = set()
    with open(path, encoding="utf-8") as f:
        lst = f.readlines()
        for line in lst:
            line = word_filter(line)
            if not line:
                continue
            # line = line.replace("\"", "«", 1).replace("\"", "»", 1)
            # line = line.capitalize()
            sorted_lst.add(line)

    with open(path, encoding="utf-8", mode="w+") as f:
        f.write("\n".join(sorted(sorted_lst)))
    return len(sorted_lst)


if __name__ == '__main__':
    # print(file_filter("../../systemd/decks/1.txt"))
    print(word_filter("<b>Alias party</b><"))
