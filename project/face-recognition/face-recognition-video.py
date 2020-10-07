# PENGGUNAAN
# python face-recognition-video.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import library yang di perlukan
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import serial

ser=serial.Serial('/dev/ttyACM0',9600)

# Parsing Argumen
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
	help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load pendeteksi wajah dari file cascade OpenCV
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# Nyalakan Kamera
print("[INFO] Memulai Stream dari Pi Camera...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

# Penghitung FPS (Frame per Second)
fps = FPS().start()

# loop dari semua frame yang di dapat
while True:
	# dapatkan frame, dan resize ke 500pixel agar lebih cepat
	frame = vs.read()
	frame = imutils.resize(frame, width=500)
	
	# Konversi ke grayscale dan konversi ke RGB
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# deteksi wajah dari frame grayscale
	rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)

   # Tampilkan kotak di wajah yang dideteksi
	boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	# loop di semua wajah yang terdeteksi
	for encoding in encodings:
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"

		# check apakah ada wajah yang di kenali
		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
			name = max(counts, key=counts.get)
		names.append(name)
		
		if name == 'Arnav' or 'Aj' or 'Alex' or 'Alyssa' or 'Ariana' or 'Dylan' or 'Elan' or 'Evan' or 'Garrett' or 'Josh' or 'Julia' or 'Lorenzo' or 'MacCullum' or 'Mariana' or 'Michael' or 'Mihai' or 'MyNameJeff' or 'Stefan':
			ser.write('g')
		if name == 'Abe' or 'Mike' or 'Aron':
			ser.write('b')
			print name
		if name != 'Arnav' or 'Al' or 'Abe' or 'Joi' or 'Mike' or 'Aron':
			ser.write('q')

	# loop di semua wajah yang sudah di kenali
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# tampilkan nama di wajah yang di kenali
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			0.75, (0, 255, 0), 2)

	# Tampilkan gambar di layar
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# tunggu tombol 1 untuk keluar
	if key == ord("q"):
		break

	# update FPS
	fps.update()

# tampilkan info FPS
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# cleanup
cv2.destroyAllWindows()
vs.stop()
