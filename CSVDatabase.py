import csv

class Database:
    def __init__(self, book, base_dir = "logs/"):
        self.last_page = 0
        self.data = list()
        self.book = book
        self.base_dir = base_dir
        if book is not None:
            try:
                with open(f"{base_dir}{book}.csv", "r") as f:
                    reader = csv.reader(f)
                    self.parse_database(reader)
            except FileNotFoundError:
                print("Book not found! Let's make a new entry for you.")
            except:  # avoid situatiosn where we accidentally wipe the file
                print("I've loaded the file but I'm having trouble reading it. Please remove it or fix it before running again!")
                quit()

    def parse_database(self, reader):
        for line in reader:
            try:
                page, marker= int(line[0]), line[1]
                if len(line) > 2:
                    comments = line[2]
                    print(f"Parsed: pg {page} | {marker} | {comments}")
                else:
                    print(f"Parsed: pg {page} | {marker}")

            except:
                print(f"Line not parsed due to error: {line}")
            self.data.append([page, marker, comments])
        self.data.sort(key=lambda x: x[0])  # just in case we messed things up last time s
        self.last_page = self.data[-1][0]

    def get_last_page(self):
        return self.last_page

    def delete_last_entry(self):
        self.data.pop()

    def add_new_entry(self, page, label):
        self.data.append([page, label])

    def add_annotation(self, annotation):
        self.data[-1].append(annotation)

    def data_dump(self):
        with open(f"{self.base_dir}/{self.book}.csv", "w", newline='') as f:
            writer = csv.writer(f, delimiter=',')
            print("******* REPORT GENERATED BELOW THIS LINE *******")
            for elem in self.data:
                writer.writerow(elem)
                print(elem)
            print("******* END OF REPORT *******")

    def __len__(self):
        return len(self.data)