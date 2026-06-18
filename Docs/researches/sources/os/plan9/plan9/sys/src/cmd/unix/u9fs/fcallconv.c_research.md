# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcallconv.c

- Role: Formats 9P `Fcall` and `Dir` structures into readable debug strings.
- Key functions: `fcallconv` handles all 9P request/response message types; `dirconv` and `fdirconv` format `Dir`; `qidtype` renders Qid flags; `dumpsome` prints read/write payload previews.
- Integration: Registered as `%F` and `%D` by `u9fs.c`; uses old or new stat decoders depending on global `old9p`.
- Risks/notes: Uses fixed-size local buffers and `sprint`; normal debug strings fit, but unusually large formatted fields could stress buffer assumptions.
