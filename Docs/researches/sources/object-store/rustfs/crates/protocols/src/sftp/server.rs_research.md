# sources/object-store/rustfs/crates/protocols/src/sftp/server.rs

## Purpose
`server.rs` is the SSH server entry point for SFTP. It owns SSH crypto preferences, host-key configuration and hot reload, TCP accept/session orchestration, password authentication against IAM, channel gating, and per-session `SftpDriver` creation.

## Important APIs, Types, and Functions
`SftpServer<S>` stores validated config, `SshConfigHolder`, cloneable storage, session registry, and process-wide read-cache accumulator. `new`, `config`, and `start` are the main lifecycle APIs. `build_preferred` and `build_ssh_config` construct password-only SSH config with AEAD ciphers, modern KEX, strict-KEX markers, non-SHA1 host keys, no compression, keepalives, idle timeout, and packet/channel sizing. `SshConfigHolder` manages current config and an order-independent host-key fingerprint. `spawn_host_key_reload_loop`, `handle_accept`, `run_session`, `drain_sessions`, and `SshSessionHandler` implement runtime behavior.

## Control Flow
`start` binds the listener, starts optional host-key reload, drains finished sessions synchronously, and uses a biased accept/shutdown select. Each accepted stream gets a `SessionDiag`, registry weak ref, child cancellation token, cloned storage, resolved limits, and on Linux a duplicated socket for the watchdog. `run_session` wraps SSH setup in a handshake deadline, spawns the watchdog after handshake, then awaits the session or cancellation. Shutdown cancels the parent token and drains session tasks within `SHUTDOWN_DRAIN_TIMEOUT_SECS`.

Authentication rejects none/public-key methods, checks access key existence and active status through `rustfs_iam`, compares secrets using `ConstantTimeEq`, and stores `SessionContext` on success. `subsystem_request` accepts only the SFTP subsystem, requires authentication and a known channel, sends channel success, builds `SftpDriver`, and runs `russh_sftp::server::run`. Other SSH channel features are explicitly rejected.

## State and Persistence Behavior
Host-key config is `RwLock<Arc<Config>>`; reload swaps only when fingerprint changes, so existing sessions keep their config and new sessions see new keys. Per-session state includes channel map, optional session context, diagnostics, and resolved limits. The read-cache accumulator is process-wide. Backend persistent state is delegated to the driver and cleaned on driver drop.

## Dependencies and Integration Points
The file depends on `russh`, `russh_sftp`, `rustfs_iam`, SFTP config/constants, lifecycle/watchdogs, `StorageBackend`, session types, Tokio listener/broadcast/join sets, `CancellationToken`, and tracing. `mod.rs` re-exports `SftpServer`.

## Risks and Test Signals
Risks include slow handshakes pinning tasks, invalid host-key reload, russh default behavior changes, shutdown delays from wedged sessions, and channel map drift. Tests cover crypto preferences, strict-KEX/ext-info markers, no SHA1 RSA, password-only auth, zero auth rejection delay, keepalive/idle config, host-key reload replacement/no-op/failure retention, and order-independent fingerprints.
