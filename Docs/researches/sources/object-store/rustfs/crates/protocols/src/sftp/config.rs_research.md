# sources/object-store/rustfs/crates/protocols/src/sftp/config.rs

Purpose: This module defines SFTP listener configuration, validation, operational env override resolution, host-key loading, and initialization errors.

Important APIs and types: `SftpInitError` covers missing/unreadable host-key directories, insecure Unix key permissions, no valid keys, invalid config, russh server errors, and unsupported platforms. `SftpConfig` includes bind address, host-key directory, idle timeout, multipart part size, handle limits, backend operation timeout, read-cache window/total memory, read-only mode, and SSH banner. Methods include `validate`, `resolve_handles_per_session`, `resolve_backend_op_timeout_secs`, `resolve_read_cache_window_bytes`, `resolve_read_cache_total_mem_bytes`, and `load_host_keys`.

Control flow: `validate` enforces `SSH-2.0-` banner prefix, positive idle timeout, S3 multipart min/max part size, and target `usize` compatibility. The resolve helpers accept `None`, return in-range overrides, and log warnings while falling back for out-of-range values; read-cache window specially accepts `0` as disabled. `load_host_keys` scans the configured directory, skips non-files, empty files, and huge files, checks Unix mode bits, reads candidate PEM strings, decodes unencrypted private keys, logs decode failures differently for key-looking vs non-key files, errors if no keys load, and sorts keys by algorithm preference then public key bytes.

State and persistence behavior: The module reads host-key files and directory metadata but writes nothing. Loaded private keys are returned in memory; comments note the private key type zeroizes on drop, while intermediate PEM strings are ordinary `String`s. Configuration values are runtime data, usually derived from environment by caller code.

Dependencies and integration points: It uses SFTP limits constants, `russh::keys`, Tokio filesystem APIs, Unix permission extensions when available, and tracing. The SFTP server startup path validates config and loads host keys before accepting clients. The operational values feed driver resource limits, timeouts, read cache behavior, and multipart flushing.

Risks: Passphrase-protected host keys are skipped rather than prompting, so an all-encrypted directory fails startup. On Windows, ACL security is trusted rather than verified in code. `HostKeyDirNotSet` exists for callers that require env presence, but this file does not read env directly. The PEM string is not zeroized. Sorting by algorithm changes offered key order, so tests pin the intended preference.

Test signals: Tests cover typical validation, bad banner, zero timeout, part-size bounds, error display, missing and empty directories, Windows key loading, Unix insecure permissions, valid Ed25519 loading, non-key/empty/passphrase-like skips, Ed25519-before-ECDSA ordering, and all resolver boundary cases for handles, backend timeout, read-cache window, disabled cache sentinel, and total memory.
