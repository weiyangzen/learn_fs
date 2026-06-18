# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/graph.c

Renders historical server statistics into in-memory PNG-ready graph images.

Key behavior:
- Initializes draw subsystem, small font, repeated color images, and fill palettes lazily under `memdrawlock`.
- `statgraph` accepts a `Graph` descriptor, chooses default dimensions, bins stats with `binstats`, computes min/max, draws axis/labels, and renders min-to-max vertical bars with two-color fills.
- Supports caller-specified min/max, time range, size, and fill palette index.

Interactions:
- Used by `httpd.c` `/graph` endpoint, then encoded with `writepng`.

Notable details:
- Uses a 2000-bin stack array and calls `needstack(8192)`.
- If graph width exceeds bin count, it is clamped.
