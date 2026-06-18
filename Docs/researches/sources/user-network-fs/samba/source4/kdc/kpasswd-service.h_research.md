## sources/user-network-fs/samba/source4/kdc/kpasswd-service.h

Purpose: public interface for Samba's kpasswd service path. It declares the common packet processor and the backend request handler implemented separately for MIT and Heimdal builds.

Important APIs and types: forward-declares `struct gensec_security`. `kpasswd_handle_request()` consumes an already unwrapped password payload plus protocol version and produces a decoded kpasswd reply or error string. `kpasswd_process()` consumes the full wire request, remote/local socket addresses, and datagram flag, then produces the full wire reply.

Control flow and integration: the header defines the contract boundary between network/GENSEC framing (`kpasswd_process`) and password operation semantics (`kpasswd_handle_request`). Only one backend implementation of `kpasswd_handle_request` should be linked.

State and persistence: no state; callers pass `kdc_server`, talloc context, and mutable `DATA_BLOB` output pointers.

Dependencies: relies on KDC server types, `DATA_BLOB`, `TALLOC_CTX`, `tsocket_address`, `krb5_error_code`, and `kdc_code` from included compilation units.

Risks: ABI/prototype drift between MIT and Heimdal C files would break build-time selection. `datagram` is exposed in `kpasswd_process` but currently not used by the implementation, so future UDP/TCP differences need care.

Test signals: compile both MIT and Heimdal configurations and verify callers include this header rather than declaring local prototypes.
