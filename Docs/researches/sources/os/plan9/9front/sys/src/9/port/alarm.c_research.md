# File Research: sources/os/plan9/9front/sys/src/9/port/alarm.c

Portable process alarm implementation.

Key behavior:
- Maintains a globally sorted linked list of processes with pending alarm times under `alarms`.
- `alarmkproc` runs as a kernel process, walks expired alarms, posts `"alarm"` notes to alive processes, clears their alarm fields, reinserts the first non-expired process, and sleeps until awakened.
- `checkalarms` is called every clock tick on CPU 0 and wakes the alarm process when the head alarm is due or invalid.
- `procalarm` implements alarm setup/cancel for the current process, returns remaining time from the previous alarm, removes any existing alarm entry, and inserts the process in deadline order.

Notable dependencies:
- Process note delivery and `Proc` alarm fields.
- Tick conversion helpers and CPU0 tick count.

Research notes:
- Alarm expiration uses signed subtraction to handle tick wraparound.
- `procalarm(0)` cancels without taking the global alarm lock after computing old remaining time.
