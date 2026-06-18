<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/protocols.rs -->
# sources/object-store/rustfs/crates/config/src/constants/protocols.rs

## Purpose
Defines FTP/FTPS, WebDAV, and SFTP protocol server environment keys and defaults, including TLS, host key, multipart upload, handle, backend timeout, and SFTP read-cache controls.

## Important APIs, types, and functions
Important constants include default FTP/FTPS/WebDAV/SFTP bind addresses, passive ports/external IP options, protocol enable/address/TLS/certs env keys, and SFTP host-key reload, idle timeout, part size, read-only, banner, handles-per-session, backend operation timeout, read cache window, and total cache memory keys. Defaults include SFTP idle timeout 600 seconds, host-key reload off, 16 MiB multipart part size, read-only false, and banner `SSH-2.0-RustFS`.

## Control flow
No executable control flow. Server startup and protocol adapters parse the env keys and enforce the documented bounds.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with FTP/FTPS/WebDAV/SFTP server crates, TLS certificate loading, S3 multipart uploads, SFTP handle accounting, backend object-store calls, and cache memory limiters.

## Risks and edge cases
SFTP host-key directory has no default, so enabling SFTP without explicit key configuration should fail clearly. Multipart part size constrains max single upload size through the 10,000-part S3 limit. Cache and handle defaults can multiply memory under many sessions. Bounds documented in comments must be enforced downstream.

## Test signals
Protocol startup tests should verify defaults, required host-key handling, SFTP part-size bounds, read-only behavior, per-session handle cap, backend timeout, and read-cache memory ceilings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/protocols.rs -->
