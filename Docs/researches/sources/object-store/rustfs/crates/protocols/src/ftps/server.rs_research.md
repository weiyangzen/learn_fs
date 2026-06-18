# sources/object-store/rustfs/crates/protocols/src/ftps/server.rs

Purpose: This module builds and runs the FTPS server around libunftp, including TLS setup, passive/active mode configuration, IAM-backed authentication, and user-detail construction for storage operations.

Important APIs and types: `FtpsUser` implements `UserDetail` and carries username, display name, and `SessionContext`. `FtpsServer<S>` owns `FtpsConfig` and a generic S3 storage backend. `FtpsUserDetailProvider` builds `FtpsUser` from IAM identity lookup. `FtpsAuthenticator` verifies access key and secret key against IAM. `FtpsServer::new`, `start`, `config`, and `storage` are the main server APIs.

Control flow: `new` validates configuration. `start` logs startup, creates a TLS reload shutdown channel, builds a `libunftp::ServerBuilder` with `FtpsDriver` factories and IAM auth, configures passive ports, optional external passive host, active/passive mode, optional TLS certificate resolver and reload loop, optional mandatory FTPS, then spawns `server.listen`. A `tokio::select!` waits for server completion/failure or broadcast shutdown, and asks the reload loop to stop either way. Authentication fetches IAM, constructs RustFS credentials from FTP username/password, checks key validity, verifies identity presence, compares stored secret key, and returns a libunftp principal.

State and persistence behavior: Runtime state includes the server task, TLS reload task, and cloned storage backend. It reads certificate material from `cert_dir` through the reloadable resolver but does not write files. IAM user identity is read during auth and user-detail phases. Session contexts use `0.0.0.0` as source IP here.

Dependencies and integration points: It depends on libunftp, unftp_core auth/detail traits, rustls with aws-lc provider, RustFS TLS reload utilities, RustFS config env keys, IAM, credential types, `MaskedAccessKey`, and shared `SessionContext`. `FtpsDriver` receives the storage clone per session.

Risks: The code stores the spawned reload task in `_reload_task` but relies on the shutdown channel rather than joining it. The comment says dropping `server_handle` closes the listener on shutdown, but in the current branch the handle is not explicitly aborted after shutdown wins the select, so graceful cancellation behavior depends on Tokio and libunftp task lifetime details. Source IP is not taken from the client connection. Secret-key comparison is direct string equality. CA file is validated in config but this server path uses `with_no_client_auth`, so client-certificate verification is not actually wired here.

Test signals: No local tests exist. Useful signals include startup validation errors, passive range application, TLS-required behavior with and without certs, reload shutdown, authentication rejection for bad key or secret, masked logging, and user-detail failure when IAM is unavailable or identity is missing.
