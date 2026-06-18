# sources/user-network-fs/rclone/backend/sftp/ssh.go

Purpose: defines abstraction interfaces that let the SFTP backend use either Go's internal SSH client or an external `ssh` binary behind the same connection/session API.

Important APIs/types/functions: `sshClient` requires `Wait`, `SendKeepAlive`, `Close`, `NewSession`, and `CanReuse`. `sshSession` requires environment setup, command/subsystem start, stdin/stdout pipes, `Run`, `Close`, and stdout/stderr writer setters.

Control flow: no executable logic. `sftp.go` consumes these interfaces when creating SFTP clients, running shell commands, detecting shell type, and managing pooled connections. `ssh_internal.go` and `ssh_external.go` provide implementations.

State and persistence behavior: none in this file; state belongs to concrete implementations.

Dependencies/integration: imports only `io` for stream interfaces. The abstraction is central to connection pooling because `CanReuse` determines whether a borrowed connection can return to the pool.

Risks/test signals: interface drift is the main risk: new behavior added to one implementation must satisfy both. Tests for external wait/close and integration tests indirectly validate the contract.
