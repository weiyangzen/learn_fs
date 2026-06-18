# sources/user-network-fs/rclone/backend/sftp/ssh_internal.go

Purpose: implements SFTP's SSH abstraction using `golang.org/x/crypto/ssh`.

Important APIs/types/functions: `sshClientInternal` wraps `*ssh.Client`; `newSSHClientInternal` dials through direct, SOCKS5, or HTTP CONNECT proxy paths and completes the SSH handshake. Methods implement waiting, OpenSSH keepalive request, close, reuse allowance, and session creation. `sshSessionInternal` embeds `*ssh.Session` and adapts stdout/stderr setters.

Control flow: `newSSHClientInternal` builds a dialer from rclone HTTP config, chooses proxy behavior from backend options, calls `ssh.NewClientConn`, logs connection metadata, and returns a reusable client. Sessions are thin wrappers over `srv.NewSession`.

State and persistence behavior: no persistence. Internal clients are reusable and therefore eligible for the SFTP connection pool.

Dependencies/integration: uses rclone `fshttp`, proxy helpers, `x/crypto/ssh`, and `net`. It is the default path when `Options.SSH` is empty.

Risks/test signals: risks include proxy dialing behavior, host-key/auth config supplied by `sftp.go`, and keepalive failures being only logged. Integration tests provide most coverage; no dedicated unit tests are present for this wrapper.
