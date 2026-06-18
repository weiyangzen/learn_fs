# File Research: sources/os/plan9/9front/sys/src/cmd/aux/kbdfs/kbdfs.c

Role: Keyboard and console 9P service implementing `/dev/kbd`, `/dev/kbdin`, `/dev/kbin`, `/dev/kbmap`, `/dev/cons`, and `/dev/consctl`.

Inputs:
- Reads either `/dev/kbd` event stream or `/dev/scancode` plus `/dev/leds`.
- Optionally reads a serial console file argument.
- Optionally writes `/dev/mousectl` and `/dev/mousein` for mouse-related key events.

Translation pipeline:
- `scanproc` converts scan codes through `kbdputsc`, tracking escape prefixes, shift/control/alt/altgr/mod4, caps/num state, and LED updates.
- `kbdiproc` handles higher-level keyboard messages and legacy raw rune strings.
- `keyproc` maintains currently down button state for `/dev/kbd`, emits raw runes for key-down events, and forwards mouse/control events.
- `runeproc` implements compose handling from `latin1.h`, including Alt sequences and hex Unicode input.
- `ctlproc` routes runes to cooked console lines, raw console output, or `/dev/kbd` depending on open state and raw mode.

Filesystem behavior:
- `cons` reads cooked or raw input and writes to stdout.
- `consctl` accepts `rawon` and `rawoff`.
- `kbd` is exclusive-open and returns key state strings plus character messages.
- `kbdin` accepts structured key/rune messages; `kbin` accepts raw scan codes.
- `kbmap` reads/writes layer/scan-code/rune mappings and resets to built-in ASCII map on OTRUNC.

Special behavior:
- Ctrl-Alt-Del triggers reboot unless shift is held, in which case shift-up is synthesized.
- `Kdel` in cooked line mode posts an interrupt note.
- The process raises priority, requests noswap, and attempts to protect itself from kill by removing write permission on its proc ctl.

Concurrency:
- Uses many Plan 9 channels and procs/threads to isolate scanning, composing, request blocking, console cooking, mouse control, and interrupt delivery.
