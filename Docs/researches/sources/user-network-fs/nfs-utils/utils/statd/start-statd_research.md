## sources/user-network-fs/nfs-utils/utils/statd/start-statd

Purpose: Shell helper used by NFS mount tooling to start `rpc.statd` if locking is requested and the daemon appears absent.

Important APIs/types/functions: Uses `/run/rpc.statd.lock` with `flock`, checks `/run/rpc.statd.pid` and `kill -0`, tries `systemctl start rpc-statd.service`, adds a runtime dependency to `remote-fs.target`, and falls back to `exec rpc.statd --no-notify`.

Control flow: Serialize invocations, exit if an existing pid is alive, prefer systemd, otherwise launch daemon directly from `/`.

State and persistence: Reads pid and lock files under `/run`; systemd runtime wants are transient.

Dependencies and integration: Invoked by mounting path; depends on systemd when available, otherwise installed `rpc.statd` in PATH.

Risks and test signals: Pid-file parsing assumes numeric content and root privileges. Tests should cover concurrent invocation, stale pid file, systemd success/failure, and fallback exec arguments.
