#!/usr/bin/python3

import argparse
from robot import Robot


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for configuring the robot.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Launches the self-driving robot with customizable settings.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--cameraId',
        help='ID of the camera to use.',
        type=int,
        default=0
    )
    parser.add_argument(
        '--frameWidth',
        help='Width of the frame to capture from the camera.',
        type=int,
        default=640
    )
    parser.add_argument(
        '--frameHeight',
        help='Height of the frame to capture from the camera.',
        type=int,
        default=480
    )
    parser.add_argument(
        '--numThreads',
        help='Number of CPU threads to use for model inference.',
        type=int,
        default=4
    )
    parser.add_argument(
        '--enableEdgeTPU',
        help='Enable EdgeTPU acceleration for AI inference.',
        action='store_true'
    )

    return parser.parse_args()


def main() -> None:
    """Initializes the robot and starts execution."""
    args = parse_arguments()

    # Create a Robot instance
    r2 = Robot()

    # Start the robot supervisor loop
    r2.supervisor.execute()


if __name__ == '__main__':
    main()