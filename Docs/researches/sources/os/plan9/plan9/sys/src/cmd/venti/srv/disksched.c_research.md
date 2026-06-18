# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/disksched.c

Implements adaptive disk scheduling knobs for background work. It tracks recent level-0 disk access and level-1 index-flush disk access via `diskaccess(level)`.

`disksched()` sets `icachesleeptime` and `arenasumsleeptime` based on recent activity. During foreground disk access, it may pause index cache flushing unless dirty pressure is high. During index flush activity, it suppresses arena summary work. When idle, it removes throttling.

The adaptive path estimates write rate and desired dirty-entry target from one minute of stats history, trying to keep the index cache around 70% dirty without interfering with foreground disk work. `manualscheduling` disables this automatic adjustment.
