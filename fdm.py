import argparse
import csv
import time

try:
    import serial
except ImportError:
    serial = None



def load_calibration(path):
    xs, ys = [], []

    with open(path, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            ys.append(float(row["gf"]))
            xs.append(float(row["counts"]))

    if len(xs) < 2:
        raise ValueError("Need at least 2 calibration points")

    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))

    denom = n * sxx - sx * sx
    if denom == 0:
        raise ValueError("Bad calibration data")

    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n

    return a, b


def apply_calibration(raw, calib):
    if calib is None:
        return raw
    a, b = calib
    return a * raw + b



class Controller:
    def __init__(self, port=None, baud=115200, timeout=1, mock=False):
        self.mock = mock

        if not mock:
            if serial is None:
                raise RuntimeError("pyserial not installed")
            self.ser = serial.Serial(port, baud, timeout=timeout)
            time.sleep(2)
        else:
            self.ser = None
            self.pos = 0
            self.force = 0
            self.dir = 1

    def write(self, cmd: str):
        if self.mock:
            print(f">>> SEND: {cmd}")
            return
        assert self.ser is not None
        self.ser.write((cmd + "\n").encode())

    def read_line(self):
        if self.mock:
            self.pos += self.dir
            self.force += 900 * self.dir
            return f"{self.pos},{self.force}"

        assert self.ser is not None
        return self.ser.readline().decode(errors="ignore").strip()



def run_test(ctrl, threshold, calib=None, debug=False):
    data = []
    state = "LOAD"

    ctrl.write("W200")
    ctrl.write("D1")

    if debug:
        print(f"Threshold: {threshold}")

    try:
        while True:
            ctrl.write("SR1")

            line = ctrl.read_line()
            if not line:
                continue

            try:
                pos_s, raw_s = line.split(",")
                pos = int(pos_s)
                raw = float(raw_s)
            except:
                continue

            force = apply_calibration(raw, calib)

            if debug:
                print(f"POS={pos} FORCE={force:.2f} gf STATE={state}")

            if state == "LOAD" and force >= threshold:
                state = "UNLOAD"
                ctrl.write("D0")
                if debug:
                    print(">>> THRESHOLD HIT → reversing")

            if state == "UNLOAD" and pos <= 0:
                if debug:
                    print(">>> RETURNED TO ZERO → stop")
                break

            data.append((pos, force, state))

    except KeyboardInterrupt:
        if debug:
            print("\nInterrupted")

    return data



def run_calibration(ctrl, samples=100, out="calib.csv"):
    print("\nCalibration mode")
    print("Enter known force in gf for each sample.")
    print("Blank input → finish\n")

    data = []

    try:
        for i in range(samples):
            inp = input(f"[{i}] gf (blank to finish): ").strip()
            if inp == "":
                break

            gf = float(inp)

            ctrl.write("R1")
            time.sleep(0.2)

            line = ctrl.read_line()
            if not line:
                continue

            try:
                _, raw = line.split(",")
                raw = float(raw)
            except:
                continue

            print(f"   raw={raw} gf={gf}")
            data.append((gf, raw))

    except KeyboardInterrupt:
        print("\nCalibration interrupted")

    if not data:
        print("No calibration data collected.")
        return

    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gf", "counts"])
        w.writerows(data)

    print(f"Saved calibration → {out}")



def save_csv(path, data):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["position", "force_gf", "state"])
        w.writerows(data)



def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")

    t = sub.add_parser("test")
    t.add_argument("--port", default="COM3")
    t.add_argument("--threshold", type=float, required=True)
    t.add_argument("--out", default="out.csv")
    t.add_argument("--mock", action="store_true")
    t.add_argument("--debug", action="store_true")
    t.add_argument("--calib", default=None)

    c = sub.add_parser("calib")
    c.add_argument("--port", default="COM3")
    c.add_argument("--out", default="calib.csv")
    c.add_argument("--mock", action="store_true")
    c.add_argument("--samples", type=int, default=100)

    args = p.parse_args()

    ctrl = Controller(port=args.port, mock=getattr(args, "mock", False))

    if args.cmd == "calib":
        run_calibration(ctrl, samples=args.samples, out=args.out)
        return

    if args.cmd == "test":
        calib = load_calibration(args.calib) if args.calib else None

        print("Running test...")

        data = run_test(
            ctrl,
            threshold=args.threshold,
            calib=calib,
            debug=args.debug
        )

        if not data:
            print("No data collected - nothing saved.")
            return

        save_csv(args.out, data)
        print(f"Saved {len(data)} rows → {args.out}")
        return

    print("No command specified")


if __name__ == "__main__":
    main()