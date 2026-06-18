# File Research: sources/os/plan9/9front/sys/src/cmd/bind.c

This is a thin command wrapper around Plan 9 `bind`.

Behavior:
- Supports `-a`, `-b`, `-c`, and `-q`.
- Rejects simultaneous `-a` and `-b`.
- Calls `bind(new, old, flags)`.
- On failure, `-q` exits successfully; otherwise it probes `new` and `old` with `access` to print a clearer diagnostic.

Filesystem/OS relevance:
- Directly manipulates the Plan 9 namespace using `bind`.
- Uses Plan 9 mount flags `MAFTER`, `MBEFORE`, and `MCREATE`.
