# Bonus

## Hack for running C++ OpenCV2 in Ubuntu terminal

```sh
sudo apt update && sudo apt install libopencv-dev
sudo cp -r /usr/local/include/opencv4/opencv2 /usr/include/
g++ main.cpp -o main `pkg-config --libs --cflags opencv4`
```
