import sys
from toio.simple import SimpleCube
import serial
import time

# 設定パラメータ（必要に応じて変更）
CONFIG = {
    "COM_PORT_1": 'COM7',       # シリアルポート設定
    "BAUD_RATE": 115200,         # ボーレート（通信速度）
    "default_speed": 30,         # デフォルトの移動速度
    "square_width": 50,          # 正方形移動の一辺の長さ
    "power": 150,                # ポンプ出力のデフォルト設定
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

# 正方形に移動する関数
def square(cube, width, speed, serial_connection):
    """正方形に移動する関数"""
    targets = ((width, width), (width, -width), (-width, -width), (-width, width), (width, width))
    print("** 正方形移動開始")
    for target in targets:
        target_pos_x, target_pos_y = target
        print(f"({target_pos_x}, {target_pos_y}) に移動")
        success = cube.move_to(speed, x=target_pos_x, y=target_pos_y)
        serial_push(CONFIG["power"], serial_connection)  # ポンプ制御
        print(f"到着ステータス: {success}")
        if not success:
            print("位置IDが認識されませんでした")
            break
        cube.sleep(0.5)

def main():
    """メイン関数：square 移動のみ実行"""
    serial_connection = setup_serial_connection(CONFIG["COM_PORT_1"], CONFIG["BAUD_RATE"])
    with SimpleCube() as cube:
        print("** キューブ接続完了")
        # square 移動パターンのみ実行
        square(cube, CONFIG["square_width"], CONFIG["default_speed"], serial_connection)

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
