# File Research: sources/os/plan9/9front/sys/src/cmd/bar.c

This is a small graphical status bar for rio/Plan 9.

Major responsibilities:
- Draws time, battery percentage, and auxiliary stdin-provided text.
- Positions/resizes its window via `/dev/wctl` according to `-p` placement and `-b` bottom mode.
- Reads theme color from `/dev/theme`.
- Reads battery data from `/mnt/pm/battery` or `/dev/battery`.
- Emits clicked item information to stdout as `buttons<TAB>item`.

Event model:
- Uses Plan 9 threads and channels for mouse, resize, keyboard, auxiliary input, and timer events.
- `timerproc` ticks roughly once per second; battery refresh is throttled to about 30 seconds.
- `auxproc` reads lines from stdin and replaces displayed auxiliary text.

Notable implementation details:
- `nanosec` prefers cycle counter timing from `_tos->cyclefreq`, falling back to `nsec`.
- Separator formatting is custom via `%|`.
- Highlighting clips the draw region over the clicked item.

Risks and caveats:
- Fixed arrays cap displayed split items at 64 and string buffers at 1024 bytes.
- Keyboard delete exits the whole thread group.
