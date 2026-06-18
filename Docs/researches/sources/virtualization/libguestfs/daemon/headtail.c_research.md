# File Research: sources/virtualization/libguestfs/daemon/headtail.c

Wraps `head` and `tail`.

Important behavior:
- Opens the guest path under chroot and pipes fd contents to command stdin.
- Shared helper returns `split_lines(out)`.
- `do_tail_n` maps negative `n` to GNU tail’s `+N` form.

Filesystem relevance: bounded text extraction from guest files without direct full-file reads in daemon code.
