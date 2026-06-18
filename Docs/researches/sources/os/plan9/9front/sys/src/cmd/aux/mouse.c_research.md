# File Research: sources/os/plan9/9front/sys/src/cmd/aux/mouse.c

`mouse` probes and configures serial mouse hardware through `/dev/eia*` and reports the detected type to `/dev/mousectl`. It supports Microsoft-compatible `M`, Type `W`, Logitech/Mouse Systems style `C`, plus direct passthrough configuration for `ps2...` and `synaptic...`.

Detection resets serial control lines, tries known baud and line settings, probes for `M`/`M3`, sends Type W configuration commands, and probes Type C with status command `s`. Baud setup uses timed writes, alarms, and a notification handler to avoid hanging on unresponsive serial devices.

Options include `-b` baud, `-d` default type, `-n` detect without writing `/dev/mousectl`, and `-D` debug dumps. Final configuration is generally `serial <port>` with optional `M` suffix for Microsoft-compatible mode.

Risk points: heavy dependence on Plan 9 serial control strings (`b1200`, `l7`, `d1`, `r1`, etc.); timeout paths exit the program; Type W 9600 support is gated by a returned configuration bit.
