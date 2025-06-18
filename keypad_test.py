import smbus
import time

# I2C 주소 (i2cdetect로 확인한 값으로 바꿔야 함)
I2C_ADDR = 0x57  # 예시 주소
bus = smbus.SMBus(1)

def read_touch_keys():
    try:
        value = bus.read_byte(I2C_ADDR)
        return value
    except Exception as e:
        print(f"에러: {e}")
        return None

while True:
    key_value = read_touch_keys()
    if key_value is not None:
        if key_value != 0:
            print(f"터치된 키값 (비트): {bin(key_value)}")
    time.sleep(0.1)