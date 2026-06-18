# File Research: sources/os/plan9/9front/sys/src/cmd/seg.c

Purpose: Reads or writes a named Plan 9 shared segment at a given offset.

Behavior:
- Flags: `-r` read, `-w` write, `-W` 2-byte access, `-L` 4-byte access; default size is 1 byte.
- Arguments: segment name, segment size, offset, and optional data for writes.
- Uses `segattach` to map the segment.
- Reads little-endian byte/word/long manually; writes by casting into mapped memory.

Risks:
- No explicit bounds check for `port + size <= segsize`.
- Write path may perform unaligned stores depending on offset.
