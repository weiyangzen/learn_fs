# File Research: sources/os/plan9/9front/sys/src/cmd/tail.c

`tail.c` implements POSIX-style `tail` plus V10 `-r` reverse mode.

Options/semantics:
- Supports `-n N`, `-c N`, `-f`, `-r`, and old `+-N[bc][fr]` suffix syntax.
- `origin` selects beginning/end, `units` selects characters/lines, and `dir` selects forward/reverse output.
- Default count is 10 lines, or effectively unlimited for reverse mode.
- Rejects incompatible reverse combinations with chars, follow, or beginning-origin.

Implementation:
- Detects seekability with `seek(fd, 0, 2)` and resets to start.
- For non-seekable input from end, `keep` buffers and trims to the desired tail.
- For non-seekable beginning-origin, `skip` discards count then copies.
- For seekable char tails, seeks directly.
- For seekable line tails, `reverse` scans backward by `Bsize` blocks to find line boundaries.
- `-f` repeatedly checks truncation with `dirfstat`, copies new data, and sleeps 5 seconds.

Risks:
- `keep` is documented as quadratic in file length times tail length.
- `count` is `long`, with explicit range checks but still constrained by platform long size.
- Reverse path uses dynamic buffers and manual line-boundary logic.
