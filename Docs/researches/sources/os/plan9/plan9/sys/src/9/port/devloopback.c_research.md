# File Research: sources/os/plan9/plan9/sys/src/9/port/devloopback.c

Implements `#X`, a configurable two-ended loopback network/link simulator. Up to five loopback instances are available; each exposes `loopbackN/0` and `loopbackN/1`, with each port containing `ctl`, `status`, `stats`, and `data`.

`Loop` owns two `Link` structures. Each `Link` has input/output queues, a transmission queue, packet/byte/drop counters, queue limits, delay settings, drop policy, and a timer. Writes to one side enqueue packets for delivery to the other side.

Control commands tune link behavior: `delay latency bytedelay`, `indrop`, `droprate`, `limit`, and `reset`. Status reports delay, queue limit, input-drop mode, and drop rate. Stats report packets, bytes, deliberate drops, and soft overflows.

Packet writes add an 8-byte timestamp header, optionally pad to `minmtu`, record counters, enqueue into the remote output queue, and call `looper`. `pushlink` moves packets through timed output and receive stages, applying per-byte and fixed latency, random drops, queue overflow behavior, and timer scheduling for future delivery.

Closing either data side hangs up the opposite output queue; when both sides are closed, queues are reopened and state reset. The device is useful for network testing with artificial latency, bandwidth serialization, drops, and queue pressure.

One source-level detail to verify during maintenance: `pushlink` references `link->delayn` while the struct field is named `delaynns`, which looks like a typo unless supplied by an external macro in this tree.
