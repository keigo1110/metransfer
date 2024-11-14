import sys
from toio.simple import SimpleCube
import math
import serial
import time

# 設定パラメータ（必要に応じて変更）
CONFIG = {
    "COM_PORT_1": 'COM7',       # シリアルポート設定
    "BAUD_RATE": 115200,         # ボーレート（通信速度）
    "default_speed": 30,         # デフォルトの移動速度
    "square_width": 50,          # 正方形移動の一辺の長さ
    "circle_diameter": 65,       # 円の直径
    "circle_divisions": 15,      # 円の分割数（移動するターゲットの数）
    "cross_width": 50,           # 十字移動の幅
    "power": 255,                # ポンプ出力のデフォルト設定
    "repeat_count": 100,         # 繰り返し回数
    "pause_duration": 20         # 各ターゲットでの停止時間（秒）
}

# シリアル通信関連の関数
def setup_serial_connection(port, baud_rate):
    """シリアル接続を設定"""
    return serial.Serial(port, baud_rate)

def serial_push(pump, connection, erase=100):
    """ポンプ制御のためのデータをシリアル通信で送信"""
    try:
        connection.write(bytes([pump]))
    except Exception as e:
        print(f"シリアル通信エラー: {e}")

# 移動関連の関数
def square(cube, width, speed, serial_connection):
    """正方形に移動する関数"""
    targets = ((width, width), (width, -width), (-width, -width), (-width, width), (width, width))
    print("** 正方形移動開始")
    for target in targets:
        target_pos_x, target_pos_y = target
        print(f"({target_pos_x}, {target_pos_y}) に移動")
        success = cube.move_to(speed, x=target_pos_x, y=target_pos_y)
        serial_push(150, serial_connection)  # ポンプ制御
        print(f"到着ステータス: {success}")
        if not success:
            print("位置IDが認識されませんでした")
            break
        cube.sleep(0.5)

def circle(cube, diameter, speed, divisions, origin, power, serial_connection):
    """円形に移動する関数"""
    targets = []
    angle_step = -360 / divisions
    for i in range(divisions):
        x = diameter * math.cos(math.radians(i * angle_step)) + origin[0]
        y = diameter * math.sin(math.radians(i * angle_step)) + origin[1]
        targets.append((x, y))
    print("** 円形移動開始")
    for target in targets:
        target_pos_x, target_pos_y = target
        print(f"({target_pos_x}, {target_pos_y}) に移動")
        success = cube.move_to(speed, x=target_pos_x, y=target_pos_y)
        serial_push(power, serial_connection)
        print(f"到着ステータス: {success}")
        if not success:
            print("位置IDが認識されませんでした")
            break
        cube.sleep(5)

def cross(cube, width, speed, serial_connection):
    """十字に移動する関数"""
    targets = ((0, 0), (width*2, 0), (-width*2, 0), (0, width), (0, -width))
    print("** 十字移動開始")
    for target in targets:
        target_pos_x, target_pos_y = target
        print(f"({target_pos_x}, {target_pos_y}) に移動")
        success = cube.move_to(speed, x=target_pos_x, y=target_pos_y)
        serial_push(100, serial_connection)
        print(f"到着ステータス: {success}")
        if not success:
            print("位置IDが認識されませんでした")
            break
        cube.sleep(0.5)

def line(cube, speed, x, y, serial_connection):
    """直線移動する関数"""
    targets = ((x, y), (x, -y), (-x, -y), (-x, y))
    print("** 直線移動開始")
    for target in targets:
        target_pos_x, target_pos_y = target
        print(f"({target_pos_x}, {target_pos_y}) に移動")
        success = cube.move_to(speed, x=target_pos_x, y=target_pos_y)
        serial_push(100, serial_connection)
        print(f"到着ステータス: {success}")
        if not success:
            print("位置IDが認識されませんでした")
            break
        cube.sleep(0.5)

def main():
    """メイン関数：複数の移動パターンを順次実行"""
    serial_connection = setup_serial_connection(CONFIG["COM_PORT_1"], CONFIG["BAUD_RATE"])
    with SimpleCube() as cube:
        print("** キューブ接続完了")
        for _ in range(CONFIG["repeat_count"]):
            # 移動パターンの選択と実行
            square(cube, CONFIG["square_width"], CONFIG["default_speed"], serial_connection)
            circle(cube, CONFIG["circle_diameter"], CONFIG["default_speed"], CONFIG["circle_divisions"], [0, 0], CONFIG["power"], serial_connection)
            cross(cube, CONFIG["cross_width"], CONFIG["default_speed"], serial_connection)
            line(cube, CONFIG["default_speed"], 100, 70, serial_connection)

            # 停止時間
            time.sleep(CONFIG["pause_duration"])

    # プログラム終了時の処理
    serial_push(0, serial_connection)  # ポンプを停止
    serial_connection.close()
    print("** 終了")

# 実行ガード
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # キーボード割り込み発生時にポンプ停止とシリアル接続終了
        serial_connection = setup_serial_connection(CONFIG["COM_PORT_1"], CONFIG["BAUD_RATE"])
        serial_push(0, serial_connection)
        serial_connection.close()
        print("** 中断されました。停止します **")
