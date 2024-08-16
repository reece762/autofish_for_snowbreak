import os
import cv2
import numpy as np
import FindWindows
import pyautogui
import time
from PIL import ImageGrab
import pygetwindow as gw

class Settings:
    @staticmethod
    def init_img(input_img):
        dist = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([10, 70, 220])
        upper_green = np.array([20, 95, 235])
        mask = cv2.inRange(dist, lower_green, upper_green)
        out = cv2.bitwise_and(input_img, input_img, mask=mask)
        return out

def find_image_in_screenshot(screenshot, template_path):
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    w, h = template.shape[1], template.shape[0]

    res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        top_left = pt
        bottom_right = (pt[0] + w, pt[1] + h)
        #cv2.rectangle(screenshot_cv, top_left, bottom_right, (0, 255, 255), 2)

        # 計算方框中心點
        center_x = (top_left[0] + bottom_right[0]) // 2
        center_y = (top_left[1] + bottom_right[1]) // 2    
        return True
        # 在方框中心繪製一個小圓點
        #cv2.circle(screenshot_cv, (center_x, center_y), 3, (0, 0, 255), -1)
    
    '''cv2.imshow('Detected', screenshot_cv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''
    return False

def create_folder_if_not_exists(directory, folder_name):
    if not os.path.exists(os.path.join(directory, folder_name)):
        os.makedirs(os.path.join(directory, folder_name)) 
        print(f'已創建 {folder_name} 文件夾')
    else:
        print(f'{folder_name} 文件夾已存在')

    
def detect_yellow_circles(image_path):
    # Read the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Hough Circle Transform to detect circles
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=40, param1=50, param2=40, minRadius=110, maxRadius=150)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle

            # Create a mask for the circular region
            mask = np.zeros_like(gray)
            cv2.circle(mask, (x, y), r, 255, 20)

            # Define the HSV range for yellow color
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])

            # Convert the image from BGR to HSV and apply the mask
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            masked_hsv = cv2.bitwise_and(hsv, hsv, mask=mask)

            # Create a mask to filter out the yellow regions
            yellow_mask = cv2.inRange(masked_hsv, lower_yellow, upper_yellow)

            # Find yellow regions on the circle and draw contours
            contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(image, contours, -1, (0, 0, 255), 2)

        # Display the image with circles and yellow markings
        cv2.imshow('Yellow Circles', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        return False
    
def detect_qtezone():
    partial_titles = ["Snowbreak", "尘白禁区"]
    found_windows = []
    # 儲存前一幀的輪廓特徵
    previous_contour_features = None
    # 儲存前5次輪廓面積的變化
    area_changes = []
    start_time = time.time()


    windows = gw.getWindowsWithTitle("")
    for window in windows:
        for title in partial_titles:   
            if title in window.title:
                found_windows.append(window)
                bbox=((window.left+window.width)/2 + 100, window.top + 200, window.left + window.width -350, (window.top + window.height)/2 + 150)
                while True:
                    screenshot1 = ImageGrab.grab(bbox)                    
                    screenshot = np.array(screenshot1)     
                    screenshot = cv2.resize(screenshot, (64,64))  
                    #cv2.imshow('QTE Zone Detection', screenshot)
                    image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
                    image = cv2.resize(image, (1000,600))
                    lower_yellow = np.array([90, 227, 178])
                    upper_yellow = np.array([100, 255, 255])#30, 255, 255

                    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
                    lower = np.array([30, 227, 178])
                    upper = np.array([179, 255, 255])
                    mask = cv2.inRange(hsv, lower, upper)
                    #masked_hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
                    imgResult = cv2.bitwise_and(hsv, hsv, mask=mask)
                    #cv2.imshow('QTE Zone Detection', imgResult)     

                    yellow_mask = cv2.inRange(imgResult, lower_yellow, upper_yellow)        
                    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    #cv2.drawContours(imgResult, contours, -1, (0, 0, 255), 2)
                    imgResult = cv2.resize(imgResult, (1000,600))
                    #cv2.imshow('QTE Zone Detection', imgResult)
                    #print(len(contours))                    

                    # 在輪廓外形改變時執行動作
                    if len(contours) == 1:
                        # 計算輪廓的面積
                        area = cv2.contourArea(contours[0]) 
                        # 將輪廓面積變化存入列表
                        area_changes.append(area)                       
                        
                        # 比較前一幀和當前幀的輪廓特徵
                        if previous_contour_features is not None:
                            if area != previous_contour_features['area']:
                                if len(area_changes) > 3:
                                    #print("輪廓外形改變！")
                                    area_changes = []
                                    pyautogui.press('space')  
                                    time.sleep(1.5) 
                        # 更新前一幀的輪廓特徵
                        previous_contour_features = {'area': area}
                
                    elif len(contours) == 0:
                        # 檢查是否已經達到3秒
                        if time.time() - start_time > 3:
                            #print("在3秒內檢測到的輪廓數量都為0,結束功能")
                            break
                    else:
                        start_time = time.time()  # 重置計時器

                        

def main():    
    directory = './'
    folder_name = 'fish_result'    
    create_folder_if_not_exists(directory, folder_name)
    cast_line_img = "png/cast_line.png"
    bite_img = "png/bite.png"
    drag_img = "png/drag.png"    
    global previous_percentage_yellow   
    FindWindows.findwindows()
    while True:
        previous_percentage_yellow = None
        screenshot_pil = FindWindows.capwindows()
        if find_image_in_screenshot(screenshot_pil, cast_line_img):
            pyautogui.press('space')
            time.sleep(1)
            start_time = time.time()       
            found_bite = False
            print('开始钓鱼')
            while time.time() - start_time < 10:  # 最多检查60秒的bite_img
                screenshot_pil = FindWindows.capwindows()
                if find_image_in_screenshot(screenshot_pil, drag_img):
                    pyautogui.press('space')
                    found_bite = True
                    print('上钓')        
                    time.sleep(1.5)                           
                    detect_qtezone()   
                    print('结算')  
                    screenshot_pil = FindWindows.capwindows() 
                    screenshot_pil.save("fish_result/result.png")
                    time.sleep(1.5) 
                    pyautogui.press('esc')

                
            if not found_bite:
                print("Error:Image not fround")
                break
            

if __name__ == "__main__":
    main()