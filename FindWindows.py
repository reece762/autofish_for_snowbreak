import pygetwindow as gw
from PIL import ImageGrab
import os
import time
import win32gui
import win32con

def findwindows():
    partial_titles = ["Snowbreak", "尘白禁区"]
    found_windows = []

    windows = gw.getWindowsWithTitle("")
    for window in windows:
        for title in partial_titles:
            if title in window.title:
                found_windows.append(window)
                hwnd = win32gui.FindWindow(None, window.title)
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
                screenshot.save(f"{title}_screenshot.png")
                #print("Saved")

    if not found_windows:
        print("Windows not found")

def capwindows():
    partial_titles = ["Snowbreak", "尘白禁区"]
    found_windows = []

    windows = gw.getWindowsWithTitle("")
    for window in windows:
        for title in partial_titles:
            if title in window.title:
                found_windows.append(window)
                screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
                #screenshot.save("png/fishing.png")
                return screenshot

    if not found_windows:
        print("Windows not found")

if __name__ == "__main__":
    capwindows()