#!/usr/bin/env python
# coding=utf-8
import os
import cv2 as cv
import math
import time


def isAgain(src):
    # 1080
    # 1920
    again = cv.imread("./again.png")
    again = cv.cvtColor(again, cv.COLOR_BGR2GRAY)
    result = cv.matchTemplate(src, again, cv.TM_CCOEFF_NORMED)
    _, v, _, _ = cv.minMaxLoc(result)
    if v > .9:
        return True
    return False


def distance(a0, a1, b0, b1):
    return int(math.sqrt(math.pow(a0 - b0, 2) + math.pow(a1 - b1, 2)))


def drawPoint(point):
    cv.circle(origin, (point[0], 600 + point[1]), 15, (255, 0, 0), 15)
    cv.circle(src, (point[0], point[1]), 15, (255, 0, 0), 15)


def otherEnd(contours, top, limit):
    """
    top与end太近了，找另一个顶部的点，与top距离最远
    """
    tt = (0, 9999)
    for li in contours:
        for pp in li:
            p = pp[0]
            if limit(p[0]) and top[1] - p[1] < 15 and abs(top[0] - p[0]) > 50 and p[1] < tt[1]:
                tt = p
    return tt


def getDis(origin, src, x, y, contours):
    """
    计算目标点距离小人的距离
    """
    # 目标是否在左边
    left = x > src.shape[1] / 2
    # 目标顶部位置
    top = (9999, 9999)
    for li in contours:
        for pp in li:
            p = pp[0]
            if top[1] > p[1] and (left and p[0] < x - 50 or not left and p[0] > x + 50):
                top = (p[0], p[1])

    end = (0, 0)
    if left:
        # 左边
        end = (9999, 9999)
        for li in contours:
            for pp in li:
                p = pp[0]
                if p[0] < x - 50 and p[1] < y and end[0] * 98 + end[1] * 169 > p[0] * 98 + p[1] * 169:
                    end = (p[0], p[1])
        drawPoint(top)
        drawPoint(end)
        td = distance(top[0], top[1], end[0], end[1])
        dy = abs(top[1] - end[1])
        dx = abs(top[0] - end[0])
        #  xie < .35 很可能是圆柱
        # xie > 5 基本是正方体
        xie = float(dy) / dx 
        if td < 10:
            # top=end=左顶点(因为颜色相似，没有找到正方开上面两条边)
            tt = otherEnd(contours, top, lambda xx: xx < x - 50)
            top = (tt[0], top[1])
        elif td < 43:
            # 小圆柱调整
            end = (end[0], end[1] + 25)
        elif td < 120 and xie < .35:
            # 圆柱调整
            top = (top[0] + 5, top[1])
            end = (end[0], end[1] + (td - 43) * 6 / 5)
        print top, end, (x, y), td, dy, dx, xie
        if abs(top[1] - end[1]) < 15 and abs(top[0] - end[0]) > 100:
            # top=左顶点 end=右顶点,(因为颜色相似，没有找到正方开上面两条边)
            end = ((top[0] + end[0]) / 2, (top[1] + end[1]) / 2)
        elif abs(top[1] - end[1]) < 50 and abs(top[0] - end[0]) > 200:
            # top=左顶点 end=右顶点,(因为颜色相似，没有找到正方开上面两条边)
            end = ((top[0] + end[0]) / 2, (top[1] + end[1]) / 2)
        else:
            # top=上顶点 end=左顶点
            end = (top[0], end[1])
    else:
        end = (0, 9999)
        for li in contours:
            for pp in li:
                p = pp[0]
                if p[1] < y and p[0] > x + 50 and end[0] * 98 - end[1] * 169 < p[0] * 98 - p[1] * 169:
                    end = (p[0], p[1])
        drawPoint(top)
        drawPoint(end)
        # 距离太近(可能是圆柱)
        td = distance(top[0], top[1], end[0], end[1])
        dy = abs(top[1] - end[1])
        dx = abs(top[0] - end[0])
        xie = float(dy) / dx
        if td < 10:
            tt = otherEnd(contours, top, lambda xx: xx > x + 50)
            top = (tt[0], top[1])
        elif td < 43:
            end = (end[0], end[1] + 25)
        elif td < 120 and xie < .35:
            top = (top[0] + 5, top[1])
            end = (end[0], end[1] + (td - 43) * 6 / 5)
        print top, end, (x, y), td, dy, dx, xie
        # 上下距离小于50 并且 左右距离大于 200
        if abs(top[1] - end[1]) < 15 and abs(top[0] - end[0]) > 100:
            end = ((top[0] + end[0]) / 2, (top[1] + end[1]) / 2)
        elif abs(top[1] - end[1]) < 50 and abs(top[0] - end[0]) > 200:
            end = ((top[0] + end[0]) / 2, (top[1] + end[1]) / 2)
        else:
            end = (top[0], end[1])

    drawPoint(end)
    drawPoint([x, y - 600])

    # print x, y, end
    dis = int(
        math.sqrt(math.pow(x - end[0], 2) + math.pow(y - end[1] - 600, 2)))
    return dis


def play(origin, src):
    player = cv.imread("./player.png")
    player = cv.cvtColor(player, cv.COLOR_BGR2GRAY)
    result = cv.matchTemplate(src, player, cv.TM_CCOEFF_NORMED)
    _, v, _, point = cv.minMaxLoc(result)

    # 小人位置
    x = point[0] + 46
    y = point[1] + 187

    # 截取图片有用信息部分
    src = src[600:, ]
    # 找边界线
    src = cv.Canny(src, 50, 50)
    src = cv.GaussianBlur(src, (3, 3), 1)
    ssrc = cv.adaptiveThreshold(
        src, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 25, 0)
    cv.imwrite("g.png", src)
    # 找边界线上所有的点
    _, contours, _ = cv.findContours(
        src, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    dis = getDis(origin, src, x, y, contours)

    cv.circle(origin, (x, y), dis, (255, 0, 0), 15)
    cv.circle(src, (x, y - 600), dis, (255, 0, 0), 15)

    cv.imwrite("b.png", origin)
    cv.imwrite("c.png", src)

    ms = int((dis + 50) * 1.3)
    os.popen("adb shell input touchscreen swipe 170 187 170 187 " +
             str(ms))
    time.sleep(1 + (ms + 500) / 1000)


count = 0

while True:
    # 获取截图
    os.popen("adb shell screencap -p  > ./screenshot.png")
    origin = cv.imread("./screenshot.png")
    # 转换为灰度图
    src = cv.cvtColor(origin, cv.COLOR_BGR2GRAY)
    cv.imwrite("d.png", src)
    if isAgain(src):
        # 失败了，退出循环
        if count > 0:
            break
        # 点击重新开始游戏
        os.popen("adb shell input touchscreen tap 540 1600")
        time.sleep(3)
    else:
        play(origin, src)
        # break
    count += 1

# def minPOI(src):
#     """ 目标大概在这个范围 """
#     src = src[730:1382, ]
#     cv.imwrite("b.png", src)
