"""
check_dbc.py - Load the DBC file and show what is inside.

Run:  python tools/check_dbc.py

What it does:
  1. Loads dbc/engine_ecu.dbc with the cantools library.
  2. Prints every message and signal (like the database view in CANalyzer).
  3. Encodes one example frame (physical values -> raw bytes) and decodes
     it again (raw bytes -> physical values). This is exactly what the ECU
     simulator will do every 100 ms.
"""

from pathlib import Path

import cantools

# Path to the DBC file, relative to this script (works from any folder).
DBC_PATH = Path(__file__).resolve().parent.parent / "dbc" / "engine_ecu.dbc"


def main():
    db = cantools.database.load_file(DBC_PATH)

    # ---- 1. Show all messages and their signals ----
    for msg in db.messages:
        cycle = f"{msg.cycle_time} ms" if msg.cycle_time else "event"
        print(f"\n0x{msg.frame_id:03X}  {msg.name}  (DLC {msg.length}, {cycle}, sender {msg.senders})")
        for sig in msg.signals:
            print(
                f"    {sig.name:24} start bit {sig.start:2}  length {sig.length:2}  "
                f"factor {sig.scale:<5} unit '{sig.unit or ''}'"
            )

    # ---- 2. Encode: physical values -> 8 raw bytes ----
    msg = db.get_message_by_name("ECM_EngineTemp")
    physical = {
        "ECM_Temp_CRC": 0,          # real CRC is calculated later in the simulator
        "ECM_Temp_Counter": 5,
        "ECM_MIL": "OFF",           # we can use the text from VAL_ directly
        "ECM_CoolantTemp": 90,      # degC  -> raw = 90 - (-40) = 130 = 0x82
        "ECM_OilTemp": 95,          # degC
        "ECM_IntakeAirTemp": "SNA", # sensor fault -> raw 0xFF
    }
    raw = msg.encode(physical)
    print(f"\nEncode ECM_EngineTemp {physical}")
    print(f"  -> raw bytes: {raw.hex(' ').upper()}")

    # ---- 3. Decode: raw bytes -> physical values ----
    decoded = msg.decode(raw)
    print(f"Decode back -> {decoded}")


if __name__ == "__main__":
    main()
