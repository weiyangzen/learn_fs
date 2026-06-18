# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_sysv.c

Read status: complete.

Purpose: compatibility routines for older System V Unix platforms that lack standard library functions.

Main logic:
- Implements `rename` by checking source existence, unlinking destination, linking source to destination, and unlinking source.
- Implements `gettimeofday` using `times`, `time`, and `HZ`, maintaining a static offset from process ticks to wall time.

Filesystem/storage relevance:
- `rename` directly affects filesystem behavior on old System V systems.
- `gettimeofday` supports time APIs used elsewhere.

Notable behavior:
- The `rename` implementation is not atomic and may briefly remove the destination before linking.
- On failure after linking, it attempts to unlink the new destination.
