import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('C:\\EV\\PROYECTO\\yolov8n-pose.pt')

# Open the video file
cap = cv2.VideoCapture(0)

# Define the connections between keypoints as shown in the image
connections = [
    [0, 1], [0, 2], [1, 3], [2, 4], 
    [5, 6], [5, 7], [6, 8], [7, 9], 
    [8, 10], [5, 11], [6, 12], [11, 12], 
    [11, 13], [12, 14], [13, 15], [14, 16]
]

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    print ("la imagen",frame)
    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)
        
        # Iterate through each result
        for result in results:
            # Check if the desired person ID is in the result
            for i, box in enumerate(result.boxes):
                if box.id == 1:  # If the box ID is 1
                    keypoints = result.keypoints[i].xy.data.cpu().numpy()  # Get the keypoints for this box
                    h, w, c = frame.shape  # Get the shape of the frame

                    # Draw keypoints
                    for kpt in keypoints:
                        for pt in kpt:
                            x, y = int(pt[0]), int(pt[1])
                            cv2.circle(frame, (x, y), radius=3, color=(0, 255, 0), thickness=-1)
                    
                    # Draw connections
                    for conn in connections:
                        for k in keypoints:                           
                            pt1 = k[conn[0]]
                            pt2 = k[conn[1]]
                            x1, y1 = int(pt1[0]), int(pt1[1])
                            x2, y2 = int(pt2[0]), int(pt2[1])
                            if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                                cv2.line(frame, (x1, y1), (x2, y2), color=(255, 0, 0))

        # Display the annotated frame
        cv2.imshow("detect", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
