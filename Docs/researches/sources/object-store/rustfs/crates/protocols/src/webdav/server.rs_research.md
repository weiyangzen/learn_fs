# sources/object-store/rustfs/crates/protocols/src/webdav/server.rs

Runs the WebDAV network server. It binds a TCP listener, optionally wraps connections in TLS, authenticates Basic credentials against IAM, constructs a WebDAV driver, and delegates requests to `dav-server`.

Important API surface: `WebDavServer<S>` stores `WebDavConfig` and storage backend. `new()` validates config. `start()` owns listener setup, TLS resolver/reload setup, accept loop, per-connection spawning, and shutdown handling. `handle_connection_impl()` runs Hyper HTTP/1 over a Tokio IO. `handle_request()` validates body size, parses Basic auth, authenticates, builds `DavHandler`, converts request/response bodies, and returns Hyper responses. `authenticate()` checks IAM access key and secret key and builds a `SessionContext`. Small helpers create unauthorized/error responses and decode base64.

Control flow: startup logs, binds, configures a reloadable certificate resolver when TLS is enabled, then loops on accepts and shutdown. Each connection is handled in a spawned task. Each request checks `Content-Length`, decodes Basic credentials, calls IAM, constructs `WebDavDriver`, collects the whole request body into bytes, delegates to `dav-server`, collects the response body, and returns it.

Server state is runtime-only. TLS certificates are loaded from `cert_dir` and may be reloaded by a background task. Authentication state comes from IAM. Object persistence is delegated through `WebDavDriver` and the storage backend. Dependencies include Hyper, Hyper-util, `dav-server`, Tokio TCP/broadcast/watch, rustls/tokio-rustls, RustFS TLS runtime/config utilities, IAM, credentials, session context, and tracing. It is re-exported from the protocols crate under the WebDAV feature.

Risks: requests and responses are fully collected in memory around `dav-server`; the request side has a `Content-Length` check but chunked bodies without a length can still be collected before driver write limits apply. `request_timeout_secs` is not visibly enforced. TLS uses `with_no_client_auth`, so `ca_file` from config is not applied. A new DAV handler is built per request, which is simple but may add overhead.

No local tests. Useful coverage would include auth success/failure, payload-too-large, chunked upload behavior, TLS config validation, graceful shutdown, and end-to-end DAV methods through a mock storage backend.
