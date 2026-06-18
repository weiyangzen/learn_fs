# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/devcons.c

Synthetic console device for the VNC environment.

Key responsibilities:
- Provides `/dev/cons`, `/dev/consctl`, `/dev/snarf`, and `/dev/winname` entries.
- Implements fixed-size circular queues for raw keyboard input and processed line input.
- Accepts keyboard runes through `kbdputc()`, encodes them as UTF-8, queues them, and echoes to the screen unless raw mode is active.
- Implements canonical line editing for backspace, control-U, newline, and control-D.
- Supports `rawon`/`rawoff` through `consctl`.
- Maintains the snarf buffer and version, replacing it on close after write.

Important behavior:
- Opening `consctl` increments a control-open count; last close disables raw mode.
- `rawon` writes a NUL wakeup byte to unblock readers.
- Snarf writes append to a temporary per-open buffer and commit on close.

Risks:
- Queues silently stop accepting bytes when full.
- `winname` is present but mode `0000` and not otherwise handled.
