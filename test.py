#!/usr/bin/python3

import argparse
from robot import Robot

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '--cameraId', help='Id of camera.', required=False, type=int, default=0)
    parser.add_argument(
            '--frameWidth',
            help='Width of frame to capture from camera.',
            required=False,
            type=int,
            default=640)
    parser.add_argument(
            '--frameHeight',
            help='Height of frame to capture from camera.',
            required=False,
            type=int,
            default=480)
    parser.add_argument(
            '--numThreads',
            help='Number of CPU threads to run the model.',
            required=False,
            type=int,
            default=4)
    parser.add_argument(
            '--enableEdgeTPU',
            help='Whether to run the model on EdgeTPU.',
            action='store_true',
            required=False,
            default=False)
    args = parser.parse_args()

    r2 = Robot()
    r2.supervisor.execute()
