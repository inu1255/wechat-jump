# 微信跳一跳

## 测试环境

Android,分辨率1080x1920

## 思路

使用 adb 工具获取屏幕截图以及模拟长按
涉及命令
``` bash 
# 获取截图，保存到当前目录的screenshot.png
adb shell screencap -p  > ./screenshot.png
# 模拟长按起点170 187,终点170,187 持续时间1000毫秒
adb shell input touchscreen swipe 170 187 170 187 1000
```
使用opencv找小人位置及目标中心点

## 效果

1. 正方体基本都能找到中心点
2. 圆柱体基本不会掉
3. 太小的圆柱可能会掉