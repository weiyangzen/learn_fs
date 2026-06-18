
# sources/user-network-fs/rclone/fstest/testserver/init.d/rclone-serve.bash

Purpose: shared lifecycle helper for scripts that start `rclone serve ...` processes.

Important APIs/types/functions: defines `PIDFILE=/tmp/${NAME}.pid`, `DATADIR=/tmp/${NAME}-data`, `stop`, `status`, and `run`. `run` creates data dir, starts command with `nohup`, writes pidfile, and disowns the process.

Control flow: concrete scripts define `start` using `run`; this helper sources `run.bash` for command dispatch/refcounting.

State/persistence: writes pidfiles, logs, and data directories under `/tmp`.

Dependencies/integration: shell job control, local rclone binary, and `run.bash`.

Risks: pid reuse is possible if pidfile is stale and process exists but is unrelated. Logs/data can persist across runs.

Test signals: `status` probes process liveness with `kill -0`; `_connect` is emitted by concrete scripts.
