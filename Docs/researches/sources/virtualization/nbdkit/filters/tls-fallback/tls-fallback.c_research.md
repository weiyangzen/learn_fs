# File Research: sources/virtualization/nbdkit/filters/tls-fallback/tls-fallback.c

This filter serves a harmless plaintext dummy export to non-TLS clients while forwarding TLS-authenticated connections to the real backend. The default message is a static 512-byte buffer, configurable with `tlsreadme`; the handle value `&message` is used as the insecure sentinel.

`.get_ready` rejects `NBDKIT_THREAD_MODEL_SERIALIZE_CONNECTIONS`, because insecure and secure connections must coexist. For non-TLS handshakes, list/default export callbacks expose only the empty export and `.open` intentionally does not call `next`, avoiding backend work and information leaks. For TLS, callbacks forward normally.

For insecure handles, the filter overrides size, block size, writability, flush, rotational, extents, multi-conn, cache, description, and pread behavior. It advertises no write-like capabilities and reads directly from the message buffer.

Risks and invariants: the security model depends on overriding every callback reachable before or during plaintext handshake so the backend is never consulted for insecure clients. `strncpy` intentionally may leave the configured message without a terminating NUL; size is fixed at the full message buffer.
