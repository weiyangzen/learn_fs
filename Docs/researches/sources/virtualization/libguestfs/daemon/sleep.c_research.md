# File Research: sources/virtualization/libguestfs/daemon/sleep.c

Simple sleep helper.

Important behavior:
- `do_sleep(secs)` calls `sleep(secs)` and always returns success.

Filesystem relevance: no direct filesystem behavior; useful for timing and daemon interaction tests.
