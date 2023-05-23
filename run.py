import argparse
from entry import generate_ply

parser = argparse.ArgumentParser(description='Generate 3D')
parser.add_argument('--prompt', type=str, help='prompt word')
parser.add_argument('--filename', type=str, help='file name', default='exmaple')
parser.add_argument('--number', type=str, help='3d file numbers', default=1)
parser.add_argument('--scale', type=str, help='guidance scale', default=15.0)

args = parser.parse_args()


if __name__ == '__main__':
    generate_ply(args.prompt, args.filename, args.number, args.scale)
