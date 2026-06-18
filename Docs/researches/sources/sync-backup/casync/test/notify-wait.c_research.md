# sources/sync-backup/casync/test/notify-wait.c

Purpose: helper executable that runs a child command and prints its PID only after the child sends `READY=1` to a temporary notify socket.

Important APIs/types/functions: sets up abstract UNIX datagram socket, exports `NOTIFY_SOCKET`, forks/execs child, polls for datagrams, watches `SIGCHLD`, `SIGINT`, `SIGTERM`, and enforces a 30-second timeout.

Control flow/state: parent owns notification socket and child pid; child resets signal mask, redirects stdout away from the parent pipe, sets environment, and execs. Parent peeks datagram size, reads complete messages, searches for `READY=1`, then prints pid and leaves the child running.

Dependencies/integration: used by FUSE, NBD, and HTTP tests to avoid racing service startup. Depends on `time-util`, `util`, and log helpers.

Risks/test signals: signal handling and abstract socket encoding are subtle. A child that exits early or never notifies fails the test deterministically with diagnostics.

Source research group: `subset-b-009122`.
