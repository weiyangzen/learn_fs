# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/disksched.c

Adaptive disk scheduling helper that throttles background index-cache and arena-summary work.

Key behavior:
- Tracks recent disk access timestamps at two levels via `lasttime[0]` and `lasttime[1]`.
- `disksched` adjusts `icachesleeptime` and `arenasumsleeptime` based on foreground disk activity, index-cache dirty fraction, and recent flush rate.
- During level-0 activity, arena sums are paused and index flushing is delayed unless dirty fraction is high.
- During level-1 activity, index flushing can continue but arena sums stay paused.
- With no recent activity, both sleep times go to zero.
- `diskaccess(level)` records current time for a disk activity level.

Interactions:
- Called from `icachewrite.c` during index flush loops.
- Disk read/write paths call `diskaccess`.

Notable details:
- `manualscheduling` disables adaptive changes.
- Uses stats history over the last minute when available.
