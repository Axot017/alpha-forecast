import pandas as pd
import csv
import os


def combine():
    input_dir = "out/nyt"
    output_file = "out/nyt_combined.csv"

    with open(output_file, "w") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["date", "headline", "lead_paragraph"]
        )
        writer.writeheader()
        writer.writerows([])

    files = os.listdir(input_dir)
    files = sorted(files)

    for file in files:
        print(f"Processing {file}")
        pd.read_csv(f"{input_dir}/{file}").to_csv(
            output_file, mode="a", header=False, index=False
        )


if __name__ == "__main__":
    combine()
