# File Research: sources/os/plan9/plan9/sys/src/cmd/unmount.c

- Role: Command wrapper around Plan 9 `unmount`.
- Behavior: Accepts either `mountpoint` or `mounted mountpoint`, preserving argument order equivalent to `mount`.
- Integration: Calls `unmount(mnted, mtpt)` and reports errors with `%r`.
- Risks/notes: Minimal command with no special edge handling beyond usage validation.
