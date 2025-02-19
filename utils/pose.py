from typing import Tuple, List
import math_util
import linalg


class Pose:
    """
    Represents a 2D pose with position (x, y) and orientation (theta).

    Provides methods for pose transformations, inversions, and unpacking.
    """

    def __init__(self, *args: float) -> None:
        """
        Initializes a Pose object with x, y coordinates and an orientation theta.

        Args:
            *args (float): Expected to be (x, y, theta).
        """
        if len(args) != 3:
            raise ValueError("Pose requires exactly three arguments: (x, y, theta)")

        self.x: float = args[0]
        self.y: float = args[1]
        self.theta: float = math_util.normalize_angle(args[2])  # Normalize theta to stay within valid range

    def transform_to(self, reference_pose: "Pose") -> "Pose":
        """
        Transforms this pose to a given reference pose.

        Args:
            reference_pose (Pose): The reference pose to transform relative to.

        Returns:
            Pose: The transformed pose.
        """
        # Decompose the current and reference pose into vectors and angles
        rel_vect, rel_theta = self.vunpack()
        ref_vect, ref_theta = reference_pose.vunpack()

        # Rotate the relative vector by the reference pose's orientation
        result_vect_d = linalg.rotate_vector(rel_vect, ref_theta)

        # Compute the new transformed position
        result_vect = linalg.add(ref_vect, result_vect_d)

        # Compute the new transformed orientation
        result_theta = ref_theta + rel_theta

        return Pose(result_vect[0], result_vect[1], result_theta)

    def inverse(self) -> "Pose":
        """
        Computes the inverse of this pose.

        Returns:
            Pose: The pose of the "world" relative to this pose.
        """
        # Invert theta and rotate the position by the negative theta
        result_theta = -self.theta
        result_pos = linalg.rotate_vector([-self.x, -self.y], result_theta)

        return Pose(result_pos[0], result_pos[1], result_theta)

    def vupdate(self, vect: List[float], theta: float) -> None:
        """
        Updates the pose using a vector (x, y) and an orientation theta.

        Args:
            vect (List[float]): The new position as a vector [x, y].
            theta (float): The new orientation.
        """
        self.x = vect[0]
        self.y = vect[1]
        self.theta = math_util.normalize_angle(theta)  # Normalize theta

    def supdate(self, x: float, y: float, theta: float) -> None:
        """
        Updates the pose using individual scalar values.

        Args:
            x (float): The new x-coordinate.
            y (float): The new y-coordinate.
            theta (float): The new orientation.
        """
        self.x = x
        self.y = y
        self.theta = math_util.normalize_angle(theta)  # Normalize theta

    def vunpack(self) -> Tuple[List[float], float]:
        """
        Unpacks the pose into its position vector and orientation.

        Returns:
            Tuple[List[float], float]: Position as a vector [x, y] and orientation theta.
        """
        return [self.x, self.y], self.theta

    def sunpack(self) -> Tuple[float, float, float]:
        """
        Unpacks the pose into individual scalar values.

        Returns:
            Tuple[float, float, float]: x-coordinate, y-coordinate, and orientation theta.
        """
        return self.x, self.y, self.theta

    def vposition(self) -> List[float]:
        """
        Returns the position component of the pose as a vector.

        Returns:
            List[float]: Position as a vector [x, y].
        """
        return [self.x, self.y]