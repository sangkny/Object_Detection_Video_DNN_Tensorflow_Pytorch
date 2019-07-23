from __future__ import division
import argparse
import time
import cv2
import sys
import torch
from darknet import Darknet
from detection_boxes_pytorch import DetectBoxes


def arg_parse():
    """ Parsing Arguments for detection """

    parser = argparse.ArgumentParser(description='Pytorch Yolov3')
    parser.add_argument("--video", dest='video', help="Path where video is located",
                        default="assets/cars.mp4", type=str)
    parser.add_argument("--config", dest="config", help="Yolov3 config file", default="data/yolov3.cfg")
    parser.add_argument("--weight", dest="weight", help="Yolov3 weight file", default="data/yolov3.weights")
    parser.add_argument("--conf", dest="confidence", help="Confidence threshold for predictions", default=0.5)
    parser.add_argument("--nms", dest="nmsThreshold", help="NMS threshold", default=0.4)
    parser.add_argument("--resol", dest='resol', help="Input resolution of network. Higher "
                                                      "increases accuracy but decreases speed",
                        default="416", type=str)
    return parser.parse_args()


def main():
    args = arg_parse()

    VIDEO_PATH = args.video

    print("Loading network.....")
    model = Darknet(args.config)
    model.load_weights(args.weight)
    print("Network successfully loaded")

    model.net_info["height"] = args.resol
    inp_dim = int(model.net_info["height"])
    assert inp_dim % 32 == 0
    assert inp_dim > 32

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    PATH_TO_LABELS = 'labels/coco.names'

    # load detection class, default confidence threshold is 0.5
    detect = DetectBoxes(PATH_TO_LABELS, conf_threshold=args.confidence, nms_threshold=args.nmsThreshold)

    # Set window
    winName = 'YOLO-Pytorch'

    try:
        # Read Video file
        cap = cv2.VideoCapture(VIDEO_PATH)
    except IOError:
        print("Input video file", VIDEO_PATH, "doesn't exist")
        sys.exit(1)

    frameCount = 0
    start = time.time()
    while cap.isOpened():
        hasFrame, frame = cap.read()

        if not hasFrame:
            break

        detect.bounding_box_yolo(frame, inp_dim, model)

        cv2.imshow(winName, frame)
        frameCount += 1
        print("FPS {:5.2f}".format(frameCount / (time.time() - start)))

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    print("Video ended")
    print("Average FPS of Video {:5.2f}".format(frameCount / (time.time() - start)))

    # releases video and removes all windows generated by the program
    cap.release()
    cv2.destroyAllWindows()


# Starting a program
if __name__=="__main__":
    main()
