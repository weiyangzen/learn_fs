# sources/sync-backup/git-lfs/ssh/connection.go

Purpose: manages long-lived pure-SSH pkt-line transfer connections, including lazy extra connections and OpenSSH control-master multiplexing.

Important APIs/types/functions: `SSHTransfer`, `NewSSHTransfer`, `startConnection`, `IsMultiplexingEnabled`, `Connection`, `ConnectionCount`, `SetConnectionCount`, `SetConnectionCountAtLeast`, `spawnConnection`, `setConnectionCount`, and `Shutdown`.

Control flow: `NewSSHTransfer` starts connection 0 immediately. `startConnection` builds the SSH command with `GetLFSExeAndArgs`, starts the subprocess, wraps stdin/stdout in pkt-line support, negotiates protocol version, and annotates failures with stderr. Additional connections are represented by nil slots and spawned lazily by `Connection(n)` under a double-checked lock.

State/persistence behavior: in-memory state tracks connection slots, mutex, config environments, metadata, operation, multiplex enabled flag, and control path. Shrinking connection counts sends `quit` and waits. Setting count to zero shuts down connection 0 and clears control path.

Dependencies/integration: uses `subprocess.ExecCommand`, pktline, tracing, `config.Environment`, and command construction in `ssh.go`.

Risks: connection slot 0 is preserved when reducing to nonzero counts. Lazy nil slots mean count is not equal to live subprocess count. Failure paths must close pipes and wait to avoid leaked processes.

Test signals: integration tests using `lfs-ssh-echo` and SSH multiplexing validate control path creation/reuse and shutdown behavior.
