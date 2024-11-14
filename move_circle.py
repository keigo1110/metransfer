import sys
from toio.simple import SimpleCube
import math
import serial
import time

# 設定パラメータ
CONFIG = {
    "COM_PORT_1": 'COM7',       # 使用するシリアルポート（必要に応じて変更）
    "BAUD_RATE": 115200,         # ボーレート（シリアル通信速度）
    "diameter": 65,              # 円の直径
    "speed": 30,                 # 移動速度
    "divisions": 15,             # 円の分割数（移動するターゲット点の数）
    "origin": [0, 0],            # 円の中心座標
    "power": 255,                # ポンプの出力（最大255）
    "circle_repeats": 100,       # 円移動を繰り返す回数
    "pause_duration": 5          # 各ターゲットでの停止時間（秒）
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
def generate_circle_targets(diameter, divisions, origin):
    """円形移動のターゲット位置を計算"""
    targets = []
    angle_step = -360 / divisions  # 負の値にして時計回りに設定
    for i in range(divisions):
        x = diameter * math.cos(math.radians(i * angle_step)) + origin[0]
        y = diameter * math.sin(math.radians(i * angle_step)) + origin[1]
        targets.append((x, y))
    return targets

def move_in_circle(cube, targets, speed, power, pause_duration, serial_connection):
    """円形のターゲットに沿ってキューブを移動させ、ポンプの出力を制御"""
    for target_pos_x, target_pos_y in targets:
        print(f"({target_pos_x}, {target_pos_y})に移動します")
        success = cube.move_to(speed, x=target_pos_x, y=target_pos_y)
        print(f"到着ステータス: {success}")
        serial_push(power, serial_connection)
        if not success:
            print("位置IDが認識されませんでした")
            break
        cube.sleep(pause_duration)

# メインの円移動実行関数
def circle_motion(config):
    """円形移動とポンプ制御のシーケンスを実行"""
    targets = generate_circle_targets(config['diameter'], config['divisions'], config['origin'])
    print("** 実行開始")

    # シリアル接続を設定
    serial_connection = setup_serial_connection(config['COM_PORT_1'], config['BAUD_RATE'])

    with SimpleCube() as cube:
        print("** 接続完了")
        for _ in range(config['circle_repeats']):
            move_in_circle(cube, targets, config['speed'], config['power'], config['pause_duration'], serial_connection)

        # 終了時にポンプ停止および原点復帰
        serial_push(0, serial_connection)  # ポンプを停止
        success = cube.move_to(config['speed'], 0, 0)
        print(f"原点に戻る: {success}")
    serial_connection.close()
    print("** 接続終了")
    print("** 終了")

# メイン実行ガード
if __name__ == "__main__":
    try:
        circle_motion(CONFIG)
    except KeyboardInterrupt:
        # キーボード割り込みが発生した場合、ポンプを停止してシリアル接続を閉じる
        serial_connection = setup_serial_connection(CONFIG['COM_PORT_1'], CONFIG['BAUD_RATE'])
        serial_push(0, serial_connection)
        serial_connection.close()
        print("** 中断されました。停止します **")
