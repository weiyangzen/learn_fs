# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/unix_bb.c

Provides optional kernel basic-block coverage registration hooks when built with `KCOV`.

Key responsibilities:
- Maintains the global `unix_bb_list` of `bb_info` records and `unix_bb_lock`.
- Defines `__bb_init_func()`, the compiler-emitted basic-block initialization hook, under `KCOV`.
- Optionally tracks test counters and last caller metadata under `KCOV_TEST`.

Behavior:
- Raises PIL with `spl8()` and tries to acquire `unix_bb_lock`.
- If the lock is unavailable on an interrupt stack, returns to avoid possible NMI-level deadlock.
- Otherwise uses `lock_set_spl()` when needed and links an uninitialized `bb_info` into `unix_bb_list`.
- Avoids ordinary C helper calls in the hook because it can be invoked from arbitrary C routines and could recurse.

Filesystem relevance:
- No direct filesystem behavior. It is kernel instrumentation infrastructure that could include filesystem object files when coverage is enabled.
