
# sources/user-network-fs/rclone/fstest/testserver/init.d/run.bash

Purpose: common command dispatcher and refcounting layer for testserver init scripts.

Important APIs/types/functions: calculates `RUN_BASE`, `RUN_ROOT`, lock/refcount/env files, `_is_running`, `_acquire_lock`, `_release_lock`, and handles `start`, `stop`, `reset`, `force-stop`, `status`.

Control flow: `start` locks, resets stale refcounts if server is gone, starts the server only for first client, caches emitted env output, increments refcount, and prints cached env. `stop` decrements and stops at zero. `reset` stops and removes state. `force-stop` unconditionally stops and zeroes refcount. `status` delegates without lock.

State/persistence: stores per-server runtime state under `${STATE_DIR:-${XDG_RUNTIME_DIR:-/tmp}/rclone-test-server}/${NAME}`.

Dependencies/integration: requires caller-defined `start/stop/status`, `flock`, and POSIX-ish bash. `testserver.Start` invokes scripts with `start` and returned cleanup invokes `stop`.

Risks: refcount correctness is central; stale lock/state files can confuse manual debugging. It uses `set -euo pipefail`, so missing variables in sourced scripts can fail quickly.

Test signals: cached env output plus refcounted server lifecycle across concurrent tests.
