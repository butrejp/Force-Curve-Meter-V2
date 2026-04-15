import argparse
import time
import csv
import serial


# =========================
# Backend Layer
# =========================

class SerialBackend:
    def send(self, cmd: str):
        raise NotImplementedError

    def read_line(self) -> str | None:
        raise NotImplementedError


class RealSerialBackend(SerialBackend):
    def __init__(self, port, baud=115200, timeout=1.0):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(2)
        self.ser.reset_input_buffer()

    def send(self, cmd: str):
        self.ser.write((cmd + "\n").encode())

    def read_line(self):
        line = self.ser.readline().decode(errors="ignore").strip()
        return line if line else None


# =========================
# PHYSICS-AWARE MOCK (FIXED)
# =========================

class MockBackend(SerialBackend):
    def __init__(self):
        self.pos = 0
        self.direction = 1  # 1 = loading, -1 = unloading

    def send(self, cmd: str):
        if cmd.startswith("D1"):
            self.direction = 1
        elif cmd.startswith("D0"):
            self.direction = -1

    def read_line(self):
        # simulate step motion
        self.pos += self.direction

        if self.pos < 0:
            self.pos = 0

        # simulated force curve (simple spring model + slight nonlinearity)
        force = int((self.pos * 900) + (0.02 * self.pos ** 2))

        return f"{self.pos},{force}"


# =========================
# Controller
# =========================

class Controller:
    def __init__(self, port, baud=115200, timeout=1.0, mock=False, debug=False):
        self.debug = debug

        if mock:
            self.backend = MockBackend()
        else:
            self.backend = RealSerialBackend(port, baud, timeout)

    def send(self, cmd: str):
        if self.debug:
            print(f">>> SEND: {cmd}")
        self.backend.send(cmd)

    def read_line(self):
        line = self.backend.read_line()
        if self.debug and line:
            print(f"<<< RX: {line}")
        return line


# =========================
# Parsing
# =========================

def parse_line(line):
    if not line:
        return None

    parts = line.split(",")
    if len(parts) != 2:
        return None

    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


# =========================
# Test Loop
# =========================

def run_test(ctrl, threshold, settle=200):
    data = []

    state = "LOAD"

    print("Running test...")
    print(f"Threshold: {threshold}")

    ctrl.send(f"W{settle}")
    ctrl.send("D1")

    try:
        while True:

            ctrl.send("SR1")
            line = ctrl.read_line()

            parsed = parse_line(line)
            if not parsed:
                continue

            pos, force = parsed

            data.append((pos, force, state))

            if ctrl.debug:
                print(f"POS={pos} FORCE={force} STATE={state}")

            # =========================
            # STATE MACHINE
            # =========================

            if state == "LOAD":
                if force >= threshold:
                    print("Threshold hit → reversing")
                    state = "UNLOAD"
                    ctrl.send("D0")

            elif state == "UNLOAD":
                if pos <= 0:
                    print("Returned to zero → stopping")
                    break

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    return data


# =========================
# CSV Output
# =========================

def save_csv(path, data):
    if not data:
        print("No data collected - nothing saved.")
        return

    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["position", "force", "state"])
        w.writerows(data)

    print(f"Saved {len(data)} rows → {path}")


# =========================
# CLI
# =========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM3")
    parser.add_argument("--threshold", type=int, default=5000)
    parser.add_argument("--settle", type=int, default=200)
    parser.add_argument("--out", default="output.csv")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    ctrl = Controller(
        port=args.port,
        mock=args.mock,
        debug=args.debug
    )

    data = run_test(ctrl, args.threshold, args.settle)
    save_csv(args.out, data)


if __name__ == "__main__":
    main()