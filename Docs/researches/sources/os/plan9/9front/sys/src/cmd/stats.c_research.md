# File Research: sources/os/plan9/9front/sys/src/cmd/stats.c

`stats.c` is a graphical Plan 9 system monitor. It displays scrolling graphs for one or more machines, reading local or imported `/dev` and `/net` statistics.

Data model:
- `Graph` stores color, rectangle, data history, label, value callback, owning `Machine`, overflow state, and high-water mark.
- `Machine` stores system name, process info, fds for `dev/sysstat`, `dev/swap`, ethernet stats, battery, temperature, previous/current counters, and a read buffer.

Metrics:
- Memory, swap, reclaim, kernel malloc, draw memory from `/dev/swap`.
- Context switches, interrupts, syscalls, faults, TLB faults/purges, load, idle, in-interrupt from `/dev/sysstat`.
- Ethernet in/out/errors/overflows from `/net/ether*/stats`.
- Battery and CPU temperature from several possible device paths.

Rendering:
- Initializes a small palette in `colinit`.
- `resize` lays out a grid of machines by graphs, titles columns, allocates history arrays, draws labels, and redraws existing data.
- `update1` scrolls graph image left, draws the newest datum, and handles overflow labels/high-water rescaling.
- Optional log scale and y-axis labels are supported.

Remote handling:
- `initmach` imports remote roots with `rimport machine / /n/<name>/` when the target name differs from `$sysname`.
- A supervisor process restarts per-machine worker processes when they exit with `restart`.

UI:
- Button 3 menu toggles graphs between add/drop.
- Keyboard `q` or Del exits.

Risks:
- Parser logic assumes current textual formats of Plan 9 stats files.
- Remote import failures intentionally exit with `restart`.
- Drawing and sampling share memory via `rfork(RFMEM)` and use display locks around UI access.
