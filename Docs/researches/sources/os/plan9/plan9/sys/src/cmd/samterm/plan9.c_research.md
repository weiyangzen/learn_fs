# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/plan9.c

Provides Plan 9 terminal integration for screen, snarf, plumbing, external files, and host I/O.

Key functions:
- `getscreen` parses `-a`, initializes draw, tab width, and clears the screen.
- `screensize` reads `/dev/screen` dimensions for scrollbar backing allocation.
- `snarfswap` exchanges host snarf text with `/dev/snarf`, respecting protocol-version snarf limits.
- `extstart`/`extproc` provide fallback external file loading when plumbing is unavailable.
- `plumbstart`, `plumbproc`, and `plumbformat` read edit plumbing messages and format them as command text.
- `hoststart`/`hostproc` continuously read host bytes into double buffers.

Behavior notes:
- `plumbopen("send")` may fail without disabling editor startup; edit input is the important receive side.
- External-load fallback creates a `/srv` endpoint name and removes it through `removeextern`.
