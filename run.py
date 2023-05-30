import argparse
from entry import text_to_3d, image_to_3d
from log import logger

parser = argparse.ArgumentParser(description='Generate 3D')
parser.add_argument('--model', type=str, help='<text|image>')
parser.add_argument('--value', type=str, help='prompt word or image path')
parser.add_argument('--filename', type=str, help='file name', default='exmaple')
parser.add_argument('--number', type=str, help='3d file numbers', default=1)
parser.add_argument('--scale', type=str, help='guidance scale', default=15.0)

args = parser.parse_args()
logger.debug('args:%s', args)

if __name__ == '__main__':
    logger.debug('args.model: %s' ,args.model)
    if args.model == 'image':
        image_to_3d(args.value, args.filename, args.number, args.scal)
    elif args.model == 'text':
        text_to_3d(args.value, args.filename, args.number, args.scale)
    else:
        logger.info('invalid model')
