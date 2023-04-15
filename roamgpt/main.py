import argparse
from pprint import pprint
from utils import generate_links

parser = argparse.ArgumentParser()
parser.add_argument(
    "--folder",
    required=True,
    help="Input folder with text files to suggest links.",
)
parser.add_argument(
    "-o",
    "--output",
    dest="output",
    help="Output JSON file to store the suggestions.",
)
parser.add_argument(
    "--berri-email",
    required=True,
    help="Email ID to be used to generate Berri.ai instances.",
)
args = parser.parse_args()

links = generate_links(args.folder, args.output, args.berri_email)
if args.output is None:
    pprint(links)
