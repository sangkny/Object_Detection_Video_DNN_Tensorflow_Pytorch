#
# Tested on following pretrained models:
# fasterrcnn_resnet50_fpn
# maskrcnn_resnet50_fpn
#
# These models are provided by pytorch framework itself
#

import argparse
import cv2
import sys
import time
from torchvision import models
import torch
from detection_boxes_pytorch import DetectBoxes


def arg_parse():
    """ Parsing Arguments for detection """

    parser = argparse.ArgumentParser(description='Pytorch Pretrained FasterRCNN')
    parser.add_argument("--video", dest='video', help="Path where video is located",
                        default="assets/cars.mp4", type=str)
    parser.add_argument("--conf", dest="confidence", help="Confidence threshold for predictions", default=0.5)

    return parser.parse_args()


def main():
    args = arg_parse()

    VIDEO_PATH = args.video

    print("Loading network.....")
    model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    # model = models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    print("Network successfully loaded")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    # class names ex) person, car, truck, and etc.
    PATH_TO_LABELS = "labels/mscoco_labels.names"

    # load detection class, default confidence threshold is 0.5
    detect = DetectBoxes(PATH_TO_LABELS, conf_threshold=args.confidence)


    # Process inputs
    winName = 'Faster-RCNN-Pytorch'
    try:
        # Read Video file
        cap = cv2.VideoCapture(VIDEO_PATH)
    except IOError:
        print("Input video file", VIDEO_PATH, "doesn't exist")
        sys.exit(1)

    while cap.isOpened():
        hasFrame, frame = cap.read()
        # if end of frame, program is terminated
        if not hasFrame:
            break

        start = time.time()
        detect.bounding_box_rcnn(frame, model=model)
        end = time.time()

        cv2.imshow(winName, frame)
        print("FPS {:5.2f}".format(1/(end-start)))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Video ended")

    # releases video and removes all windows generated by the program
    cap.release()
    cv2.destroyAllWindows()


# Starting a program
if __name__=="__main__":
    main()
