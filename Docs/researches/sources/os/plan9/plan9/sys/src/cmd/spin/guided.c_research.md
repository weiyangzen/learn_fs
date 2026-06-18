# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/guided.c

SPIN guided simulation trail replay.

Key behavior:
- Locates a trail file using explicit `-k` name or fallback names based on the model filename.
- Warns if the source model is newer than the trail file.
- Replays trail records as process/transition steps against the parsed model.
- Handles cycle markers, claim starts, merge markers, process termination, and depth cutoff.
- Evaluates normal and `d_step` transitions while printing requested verbose/global/local state output.

Important details:
- Supports xspin and columnated output modes.
- Can skip never-claim steps when configured.
- `lost_trail()` prints remaining trail data when replay desynchronizes.
- `pc_value()` returns the current sequence number for a process id expression.

Filesystem relevance:
- Direct only for reading `.trail`/`.tra` files and checking source/trail mtimes.
