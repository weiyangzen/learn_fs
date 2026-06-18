# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/httpd.c

Built-in HTTP admin server for Venti status, control, graphs, logs, disk/debug views, and static files.

Key behavior:
- `httpdinit` registers endpoints: `/stats`, `/index`, `/storage`, `/xindex`, cache flush/kick/empty routes, `/graph`, `/set`, `/log`, `/disk`, `/debug`, and `/proc/`.
- `listenproc` announces, accepts connections, and starts one `httpproc` per connection.
- `httpproc` parses requests, dispatches by exact or prefix route, falls back to static file serving from `webroot`, supports keep-alive/chunking.
- `hsettype`, `hsethtml`, `hsettext`, and `hnotfound` handle HTTP response boilerplate.
- `fromwebdir` serves static files, blocks `..`, defaults directories to `index.html`, and chooses content type by extension.
- `/set` reads or writes runtime integer tunables including compression, devnull writes, logging, stats, scheduling, Bloom ignore, sync writes, and icache prefetch.
- `/storage` and `/index` summarize arena/index state.
- Cache routes empty, kick, or flush lump/disk/index caches.
- `/graph` renders stat graphs as PNG or text, supporting raw/diff/pct/bandwidth graph functions.
- `/log` lists and dumps Venti logs.
- `/xindex` emits XML index data.
- Also contains XML helper attribute writers and HTTP log rendering helpers.

Interactions:
- Calls `hdisk`, `hdebug`, `hproc`, `statgraph`, `writepng`, cache maintenance functions, and stats history.
- `graphname` must stay in sync with the stats enum in `dat.h`.

Notable details:
- No authentication or authorization is visible in this file; endpoints can mutate runtime settings and flush caches.
- `fromwebdir` path filtering is minimal: only `..` substring is rejected.
- `/stats` body is mostly commented out; current handler mainly sets text response and flushes.
