# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/stats.js

Purpose: Client-side JavaScript for the Venti HTTP statistics dashboard.

Key behavior:
- Defines graph URL/name mappings for disk/network/I/O bandwidth, arena/index I/O, bloom filter, disk cache, index cache, lump cache, RPC timing, and stalls.
- Builds three graph columns and two large selected graphs via DOM table manipulation and `/graph?...` image URLs.
- Handles click selection of small graphs to replace the large graph.
- Renders settings links for logging, stats, compression mode, index/storage pages, and log pages.
- Sends setting changes by navigating a hidden frame to `/set/name/value`.

Dependencies:
- Expects server endpoints `/graph`, `/set`, `/index`, `/storage`, and `/log/...`.

Notable details:
- Uses old pre-modern JavaScript style: global variables, `new Array`, inline `javascript:` URLs, and `innerHTML`.
