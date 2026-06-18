## sources/user-network-fs/libtirpc/src/debug.c

Purpose: Provides global debug-level and logging behavior for libtirpc.

Important APIs and control flow: `libtirpc_set_debug(char *name, int level, int use_stderr)` clamps negative levels to zero, chooses stderr or syslog, optionally calls `openlog`, stores the global level, and emits a level-1 startup message via `LIBTIRPC_DEBUG`. `libtirpc_log_dbg` formats variadic messages to stderr with newline or to syslog `LOG_NOTICE`.

State and persistence: `libtirpc_debug_level` and `log_stderr` are process-global mutable variables. They are not protected by a lock.

Dependencies and integration: Used by broadcast, public-key, key, and netname helper code through the macro in `debug.h`. Exported privately in `libtirpc.map.in`.

Risks and test signals: Races are possible if debug settings change while other threads log. Tests should verify negative clamp, stderr/syslog selection, message thresholding through the macro, and format handling.
