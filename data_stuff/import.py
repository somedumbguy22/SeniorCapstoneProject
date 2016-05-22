import json
import urllib
import os
import glob
import string

IMPORT_PATH = "."

def clean(value):
    return filter(lambda x: x in string.printable, value.split(":", 1)[1].strip('" \t\n\r'))

def make_comment(value):
    try:
        return clean(" ".join(value).strip())
    except:
        return ""

items = []

for root,dirs,files in os.walk(IMPORT_PATH):
    for file in files:
        if file.endswith(".txt"):
            p = os.path.join(root, file)
            data = open(p).readlines()

            name = clean(data[0].strip())
            image = clean(data[1].strip())

            image_data = "data:image/png;base64,%s" % urllib.quote(open(os.path.join(root, image), "rb").read().encode("base64"))

            price = clean(data[2].strip())

            collect = []
            for i, line in enumerate(data[3:]):
                if line.strip().lower().startswith("condition"):
                    break
                if line.strip():
                    collect.append(line.strip())

            i += 3
            description = make_comment(collect)

            condition = clean(data[i].strip())

            collect = []
            ratings = []
            rating = None
            user = None
            for i, line in enumerate(data[i + 1:]):
                l = line.strip().lower()
                if l.startswith("rating") and not l.startswith("ratingt"):
                    if collect:
                        collect = make_comment(collect)
                        if collect:
                            ratings.append((rating, user, collect))
                        collect = []
                    rating = clean(line)
                elif l.startswith("user"):
                    user = clean(line)
                else:
                    collect.append(line)

            ratings.append((rating, user, make_comment(collect)))

            items.append((name, image_data, price, description, condition, ratings))

open("output.txt", "w").write(json.dumps(items))
