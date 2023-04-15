import argparse
from pprint import pprint
from utils import generate_links

parser = argparse.ArgumentParser()
parser.add_argument("--folder", required=True)
parser.add_argument("-o", "--output", dest="output")
args = parser.parse_args()

links = generate_links(args.folder, args.output)
if args.output is None:
    pprint(links)
