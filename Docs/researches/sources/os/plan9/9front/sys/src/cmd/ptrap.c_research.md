# File Research: sources/os/plan9/9front/sys/src/cmd/ptrap.c

9P filter filesystem for plumber ports. It mounts over `/mnt/plumb`, proxies underlying plumb files, and filters read messages by port regex and optional attribute regexes. Matching plumb messages are repacked and returned; nonmatching messages are consumed.

Key behavior:
- Parses arguments as `port regex [ +attr regex ... ] ...`, with `!` prefix for inversion.
- `ptrapwalk1/open/stat/wstat` proxy the underlying `/mnt/plumb/<port>` files.
- `ptrapread/write` delegate blocking I/O to reusable IO processes so the 9P server remains responsive.
- `filterread` reads partial plumb messages, unpacks them, applies filters, and buffers packed matching messages across reads.
- `flush` interrupts the IO process handling an old request.

Integration points:
- Uses Plan 9 `thread`, `9p`, `plumb`, and `regexp` libraries.
- Mounts via `threadpostmountsrv(..., "/mnt/plumb", MREPL | MCREATE)`.

Risks:
- Attribute filter inversion uses `f->attr->invert` instead of the current `a->invert`, so multiple attribute filters may apply the wrong invert flag.
- `fname` uses a static allocated path; safe for sequential use but not inherently thread-safe.
- Filtering consumes nonmatching plumb messages, which is intended but operationally significant.
