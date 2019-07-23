#
# Tested on following pretrained models:
# faster_rcnn_resnet101_coco_2018_01_28
# faster_rcnn_inception_v2_coco_2018_01_28
#
#

import cv2
import sys
import imutils
import argparse
from detection_boxes import DetectBoxes

def arg_parse():
    """ Parsing Arguments for detection """

    parser = argparse.ArgumentParser(description='Pytorch Yolov3')
    parser.add_argument("--video", dest='video', help="Path where video is located",
                        default="assets/cars.mp4", type=str)
    parser.add_argument("--pbtxt", dest="pbtxt", help="pbtxt file", default="faster_rcnn_resnet101_coco_2018_01_28/graph.pbtxt")
    parser.add_argument("--frozen", dest="frozen", help="Frozen inference pb file", default="faster_rcnn_resnet101_coco_2018_01_28/frozen_inference_graph.pb")
    parser.add_argument("--conf", dest="confidence", help="Confidence threshold for predictions", default=0.5)
    return parser.parse_args()


def main():
    args = arg_parse()

    VIDEO_PATH = args.video

    print("Loading network.....")
    net = cv2.dnn.readNetFromTensorflow(args.frozen, args.pbtxt)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    print("Network successfully loaded")

    # class names ex) person, car, truck, and etc.
    PATH_TO_LABELS = "labels/mscoco_labels.names"

    # load detection class, default confidence threshold is 0.5
    detect = DetectBoxes(PATH_TO_LABELS, confidence_threshold=args.confidence)

    # Set window
    winName = 'Faster-RCNN-Opencv-DNN'

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

        # Resizing given frame to increase process time
        # frame = imutils.resize(frame, width=450)

        # Create a 4D blob from a frame.
        blob = cv2.dnn.blobFromImage(frame, swapRB=True, crop=False)

        # Set the input to the network
        net.setInput(blob)

        # Runs the forward pass
        network_output = net.forward()

        # Extract the bounding box and draw rectangles
        detect.detect_bounding_boxes(frame, network_output)

        # Efficiency information
        t, _ = net.getPerfProfile()
        elapsed = abs(t * 1000.0 / cv2.getTickFrequency())
        label = 'Time per frame : %0.0f ms' % elapsed
        cv2.putText(frame, label, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0))

        cv2.imshow(winName, frame)
        print("FPS {:5.2f}".format(1000 / elapsed))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Video ended")

    # releases video and removes all windows generated by the program
    cap.release()
    cv2.destroyAllWindows()


if __name__=="__main__":
    main()
