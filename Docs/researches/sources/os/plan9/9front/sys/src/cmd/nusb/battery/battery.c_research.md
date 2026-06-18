# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/battery/battery.c

USB HID battery driver exposing a synthetic battery status file.

Key elements:
- Opens interrupt IN endpoints on a USB HID battery-like device.
- Retrieves and parses the HID report descriptor, switching to report protocol when available.
- Implements generic HID report descriptor parsing with global/local/main item state, collections, push/pop, usage ranges, and report IDs.
- `itemparse` extracts input values from report packets and maps selected HID usages to battery state fields.
- Tracks remaining/full/design/warning capacity, voltage/design voltage, runtime, missing/critical/charging/discharging states.
- `hidwork` reads interrupt reports continuously, parses them under a battery lock, and updates shared state.
- Exposes `battery` read-only file through `threadpostsharesrv`.
- `fsread` prints percentage, units, capacities, warning thresholds, voltages, runtime, and textual state.

Notable behavior:
- Defaults capacity unit to `%` and full capacity to 100.
- If full/design capacity are missing or zero, they are normalized to usable defaults.
- Runtime is formatted as `HH:MM:SS`.
- Multiple interrupt endpoints can start reader processes against the same global battery state.

Risks and quirks:
- The file prints `warncapacity` twice in the numeric fields.
- HID usage handling is selective; unknown but valid battery usages are ignored.
- After repeated endpoint read errors, the driver exits all threads.
