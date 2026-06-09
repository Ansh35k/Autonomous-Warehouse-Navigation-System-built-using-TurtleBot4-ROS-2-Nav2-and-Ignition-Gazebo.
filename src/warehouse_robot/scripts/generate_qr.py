import qrcode
import os

codes = {
    "RACK_A1":    "~/warehouse_ws/src/warehouse_robot/models/qr_rack_a1/materials/textures/qr.png",
    "RACK_A2":    "~/warehouse_ws/src/warehouse_robot/models/qr_rack_a2/materials/textures/qr.png",
    "RACK_B1":    "~/warehouse_ws/src/warehouse_robot/models/qr_rack_b1/materials/textures/qr.png",
    "RACK_B2":    "~/warehouse_ws/src/warehouse_robot/models/qr_rack_b2/materials/textures/qr.png",
    "DROPZONE_1": "~/warehouse_ws/src/warehouse_robot/models/qr_dropzone_1/materials/textures/qr.png",
}

for data, path in codes.items():
    path = os.path.expanduser(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = qrcode.make(data)
    img.save(path)
    print(f"Saved {data} -> {path}")
