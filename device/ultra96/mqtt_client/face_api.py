# -*- coding: UTF-8 -*-
#-----获取人脸样本------
#-Obtian Face Samples -
import cv2
import face_recognition
import time
from matplotlib import pyplot as plt 
import threading

face_ids = set()
source_list = ['obama.jpg']
# 照片不要大于200K
# the volume of picture should be less than 200 KB
# source_list = ['zyc.jpg', 'xjt.jpg']
known_encodings = []

def encode_face(source_path):
    known_source_image = face_recognition.load_image_file(source_path)
    source_face_encoding = face_recognition.face_encodings(known_source_image)[0]
    known_encodings.append(source_face_encoding)

def get_image(cap):
    if cap or cap.isOpened() is False:
        exit('Camera is not opened!')
    success,img = cap.read()  
    if success is True: 
        return img
    else:   
        return None

def crop_face(img, face_location):
    ret = []
    for (x, y, w, h) in face_location:
        sub_img = img[x:x+w,y:y+h]
        ret.append(sub_img)
    return ret

def get_face(cap, face_id, count, cascade = './haarcascade_frontalface_alt2.xml'):
    # -----------------!---------------- NOTE ------------------!--------------
    # Call the notebook built-in camera, the parameter is 0, 
    # if there are other cameras, you can adjust the parameter cap to 1,2
    # --------------------------------------------------------------------------
    # Call the face classifier and adjust it according to the actual path
    # If you change this, be sure to change the classifier in the recognition file
    face_detector = cv2.CascadeClassifier(cascade)
    while True:
        img = get_image(cap)
        if img is None:
            continue
        # Convert to gray image to improve accuracy
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        time.sleep(0.1)
        # Where img is the gray image to be detected, 
        # 1.2 is the ratio of each image size reduction, and 
        # 5 is minNeighbors
        faces = face_detector.detectMultiScale(img, 1.2, 5)
        if len(faces):
            if face_id:
                filepath = "./face_"+str(face_id)+"/"+str(count)
                source_list.append(filepath)
                cv2.imwrite(filepath + ".jpg", img)
            break
    return img,faces

def rec_unknown(img):
    image_to_test_encoding = face_recognition.face_encodings(img)[0]
    # See how far apart the test image is from the known faces
    face_distances = face_recognition.face_distance(known_encodings, image_to_test_encoding)
    for i, face_distance in enumerate(face_distances):
        if face_distance < 0.5:
            return source_list[i][:source_list[i].rfind('.')].split("/")[0]
        else:
            return None

def add_face(get_face_num, video_in):
    cap = cv2.VideoCapture(video_in)
    # Mark the face ID
    face_id = input('\nPlease Input User name, and Look at the camera and wait ...\n')
    face_ids.add(face_id)
    # Frame selection of faces, for loop to ensure 
    # a real-time dynamic video stream that can be detected
    for i in range(get_face_num):
        get_face(cap, face_id, i)
    # release the camera
    cap.release()


def detect(video_in):
    cap = cv2.VideoCapture(video_in)
    while True:
        img,face = get_face(cap,None,0)
        face_id = rec_unknown(img)
        if face_id:
            # TODO 识别到熟人
            # TODO recognize the owner
            return img,face_id
        else:
            # TODO 识别到生人
            # TODO recognize the stranger
            return img,None



# # for source in source_list:
# #     known_source_image = face_recognition.load_image_file(source)
# #     source_face_encoding = face_recognition.face_encodings(known_source_image)[0]
# #     known_encodings.append(source_face_encoding)

# def getFace(model=0, cascade = './haarcascade_frontalface_alt2.xml'):
#     #调用笔记本内置摄像头，参数为0，如果有其他的摄像头可以调整参数为1,2
#     cap = cv2.VideoCapture(model)
#     #调用人脸分类器，要根据实际路径调整
#     # 如果更改此处，务必更改识别文件里的分类器
#     face_detector = cv2.CascadeClassifier(cascade) 
#     if cap is None or cap.isOpened() is False:
#         exit('Camera is not opened!')
#     #为即将录入的脸标记一个id
#     face_id = input('\nPlease Input User name, and Look at the camera and wait ...\n')
#     #从摄像头读取图片
#     success,img = cap.read()  
#     #转为灰度图片，减少程序符合，提高识别度
#     if success is True: 
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
#     else:   
#         return
#     #检测人脸，将每一帧摄像头记录的数据带入OpenCv中，让Classifier判断人脸
#     #其中gray为要检测的灰度图像，1.2为每次图像尺寸减小的比例，5为minNeighbors
#     time.sleep(0.1)
#     faces = face_detector.detectMultiScale(img, 1.2, 5)  
#     #框选人脸，for循环保证一个能检测的实时动态视频流
#     for (x, y, w, h) in faces:
#         cv2.imwrite(r"./"+str(face_id)+str(count)+'.jpg',img) 
#         #显示图片
#         plt.figure(str(face_id)+str(count))
#         plt.imshow(img)       
#     #关闭摄像头，释放资源
#     cap.release()


# def get_unknown(model=2, cascade = './haarcascade_frontalface_alt2.xml'):
#     #调用笔记本内置摄像头，参数为0，如果有其他的摄像头可以调整参数为1,2
#     cap = cv2.VideoCapture(model)
#     #调用人脸分类器，要根据实际路径调整
#     # 如果更改此处，务必更改识别文件里的分类器
#     face_detector = cv2.CascadeClassifier(cascade) 
#     if cap is None or cap.isOpened() is False:
#         exit('Camera is not opened!')
#     #sampleNum用来计数样本数目
#     count = 0
#     while True:    
#         #从摄像头读取图片
#         success,img = cap.read()  
# #         print(success)
#         #转为灰度图片，减少程序符合，提高识别度
#         if success is True: 
#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
#         else:   
#             break
#         #检测人脸，将每一帧摄像头记录的数据带入OpenCv中，让Classifier判断人脸
#         #其中gray为要检测的灰度图像，1.2为每次图像尺寸减小的比例，5为minNeighbors
# #         time.sleep(0.1)
#         faces = face_detector.detectMultiScale(img, 1.2, 5)  
#         #框选人脸，for循环保证一个能检测的实时动态视频流
#         for (x, y, w, h) in faces:
#             #xy为左上角的坐标,w为宽，h为高，用rectangle为人脸标记画框
# #             cv2.rectangle(img, (x, y), (x+w, y+w), (255, 0, 0))
#             #成功框选则样本数增加
#             count += 1  
#             print(count)
#             #保存图像，把灰度图片看成二维数组来检测人脸区域
#             #(这里是建立了data的文件夹，当然也可以设置为其他路径或者调用数据库)
#             cv2.imwrite(r"./unknown.jpg",img) 
#             #显示图片
#             plt.imshow(img)       
#             #保持画面的连续。waitkey方法可以绑定按键保证画面的收放，通过q键退出摄像
#         k = cv2.waitKey(1)        
#         if k == '27':
#             break        
#         elif count >= 1:
#             break
#     #关闭摄像头，释放资源
#     cap.release()
# #     cv2.destroyAllWindows()

# def rec_unknown():
#     start = time.perf_counter()
#     # Load a test image and get encondings for it
#     image_to_test = face_recognition.load_image_file('unknown.jpg')
#     image_to_test_encoding = face_recognition.face_encodings(image_to_test)[0]
#     # See how far apart the test image is from the known faces
#     face_distances = face_recognition.face_distance(known_encodings, image_to_test_encoding)
#     end = time.perf_counter()
#     print("Times: ", end - start)
#     for i, face_distance in enumerate(face_distances):
#         if face_distance < 0.5:
#             print('This is ' + source_list[i].split('.')[0])
#         else:
#             print("Unknown")
