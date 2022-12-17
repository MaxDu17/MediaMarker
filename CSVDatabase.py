import csv

class Database:
    def __init__(self, subject, base_dir = "logs/"):
        self.last_page = 0
        self.data = list()
        self.subject = subject
        self.base_dir = base_dir
        if subject is not None:
            try:
                with open(f"{base_dir}{subject}.csv", "r") as f:
                    reader = csv.reader(f)
                    self.parse_database(reader)
            except FileNotFoundError:
                print("Subject not found! Let's make a new entry for you.")
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
                    self.data.append([page, marker, comments])
                else:
                    print(f"Parsed: pg {page} | {marker}")
                    self.data.append([page, marker])

            except:
                print(f"Line not parsed due to error: {line}")
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

    def data_dump(self, to_string = None):
        with open(f"{self.base_dir}/{self.subject}.csv", "w", newline='') as f:
            writer = csv.writer(f, delimiter=',')
            print("******* REPORT GENERATED BELOW THIS LINE *******")
            for elem in self.data:
                writer.writerow(elem)
                if to_string is None:
                    print(elem)
                else:
                    # accomodates the counter for time, which needs to be parsed
                    print(to_string(elem[0]),elem[1:])
            print("******* END OF REPORT *******")

    def __len__(self):
        return len(self.data)