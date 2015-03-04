#!/usr/bin/env python

import argparse
import logging
import requests
import os
import glob
from urlparse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Add audio files from audio-path to specified work queue')
    parser._optionals.title = "Options"

    parser.add_argument('-s', '--hostname', help='The web api hostname.',
                        type=str, required=True)
    parser.add_argument('-p', '--port', help='The web api port.',
                        type=str, required=True)
    parser.add_argument('-src', '--work-queue', help='The queue to add work to',
                        type=str, required=True)
    parser.add_argument('-a', '--audio-path', help='Directory to find audio in (must be mulaw 8bit/8kHz)',
                        type=str, required=True)
    parser.add_argument('-c', '--chunk', help='ChunkID',
                        type=int, default=1, required=False)
    parser.add_argument('-l', '--lang', help='STT Language to run',
                        type=str, default='english', required=False)
    parser.add_argument('-n', '--name', help='Name of audio data',
                        type=str, required=True)
    return parser.parse_args()


def main():
    args = parse_arguments()

    api_connection = "http://%s:%s" % (args.hostname, args.port)

    abs_path = os.path.abspath(args.audio_path)
    basename = os.path.splitext(os.path.basename(abs_path))[0]
    logger.info("Working with %s" % basename)

    data = dict(chunkid=args.chunk, language=args.lang, name=args.name, queue=args.work_queue)
    files = {'bytes ': open(abs_path, 'rb')}
    requests.post(api_connection + "/fileup", data=data, files=files)


if __name__ == '__main__':
    main()
