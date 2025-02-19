class Pose:
    def __init__(self, *args):
        x = args[0]
        y = args[1]
        theta = args[2]

        self.x = x
        self.y = y
        self.theta = math_util.normalize_angle(theta)

    # get a new pose given by this pose transformed to a given reference pose
    def transform_to(self, reference_pose):
        (
            rel_vect,
            rel_theta,
        ) = self.vunpack()  # elements of this pose (the relative pose)
        ref_vect, ref_theta = reference_pose.vunpack()  # elements of the reference pose

        # construct the elements of the transformed pose
        result_vect_d = linalg.rotate_vector(rel_vect, ref_theta)
        result_vect = linalg.add(ref_vect, result_vect_d)
        result_theta = ref_theta + rel_theta

        return Pose(result_vect, result_theta)

    # get a new pose given by inverting this pose, e.g. return the pose of the "world"
    # relative to this pose
    def inverse(self):
        result_theta = -self.theta
        result_pos = linalg.rotate_vector([-self.x, -self.y], result_theta)

        return Pose(result_pos, result_theta)

    # update pose using a vector
    def vupdate(self, vect, theta):
        self.x = vect[0]
        self.y = vect[1]
        self.theta = math_util.normalize_angle(theta)

    # update pose using scalars
    def supdate(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = math_util.normalize_angle(theta)

    # return the constituents of this pose with location as a vector
    def vunpack(self):
        return [self.x, self.y], self.theta

    # return the constituents of this pose as all scalars
    def sunpack(self):
        return self.x, self.y, self.theta

    # return the position component of this pose as a vector
    def vposition(self):
        return [self.x, self.y]
