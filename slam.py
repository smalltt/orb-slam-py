import pdb
import numpy as np
import cv2

from vo import FeatureExtractor
from vo import PoseEstimator
from renderer import Renderer


class FrameDisplay(object):

    def __init__(self, path):
        self.offsets = (200, 500)
        self.path = path

        self.extractor = FeatureExtractor()
        self.pose_estimator = PoseEstimator()
        self.renderer = Renderer()

    def draw(self):
        # read video frame by frame
        vidcap = cv2.VideoCapture(self.path)
        success, frame = vidcap.read()

        window = cv2.namedWindow("video", cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow("video", *self.offsets)

        while success:
            success, frame = vidcap.read()
            if success:
                frame = self.process_frame(frame)
                cv2.imshow("video", frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

        vidcap.release()
        cv2.destroyAllWindows()

    def process_frame(self, frame):
        # frame preprocessing
        frame = cv2.transpose(frame)
        frame = cv2.flip(frame, 1)

        # extract keypoints from latest two frams and match them
        point_pairs = self.extractor.extract(frame)
        if not len(point_pairs):
            return frame

        # estimate pose from point_pairs
        point_pairs, points3d = self.pose_estimator.estimate(point_pairs)
        self.renderer.queue.put(points3d)

        # plot
        for p1, p2 in point_pairs:
            cv2.line(frame, tuple(p1), tuple(p2), (0, 255, 0))
            cv2.circle(frame, tuple(p2), 3, (0, 255, 0))
        return frame


def main():
    path = "./test.mp4"
    display = FrameDisplay(path)
    display.draw()


if __name__ == "__main__":
    main()

