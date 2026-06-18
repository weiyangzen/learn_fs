# sources/user-network-fs/libnfs/lib/libnfs-zdr.c

## Purpose

`libnfs-zdr.c` provides libnfs's built-in in-memory ZDR/XDR subset and ONC RPC message marshalling helpers. It exists so the project can encode and decode rpcgen-compatible NFS, mount, portmap, and RPCSEC_GSS messages from memory buffers without depending on a platform XDR implementation. It also creates and destroys AUTH credentials for AUTH_NONE, AUTH_UNIX, and, when Kerberos support is compiled in, AUTH_GSS.

## Important APIs, Types, and Functions

The file manages `ZDR` streams with `libnfs_zdrmem_create`, `libnfs_zdr_destroy`, `libnfs_zdr_setpos`, `libnfs_zdr_getpos`, `libnfs_zdr_getsize`, and `libnfs_zdr_getptr`. Decode-time allocations are tracked in a private linked list of `struct zdr_mem`; `zdr_malloc` allocates stream-owned memory and `libnfs_zdr_destroy` releases it.

Primitive codecs include `libnfs_zdr_u_int`, `libnfs_zdr_int`, `libnfs_zdr_uint64_t`, `libnfs_zdr_int64_t`, `libnfs_zdr_bool`, `libnfs_zdr_enum`, `libnfs_zdr_void`, `libnfs_zdr_opaque`, `libnfs_zdr_bytes`, `libnfs_zdr_string`, `libnfs_zdr_pointer`, `libnfs_zdr_array`, and `libnfs_zdr_vector`. RPC envelope helpers are `libnfs_opaque_cred`, `libnfs_opaque_verf`, `libnfs_rpc_call_body`, `libnfs_accepted_reply`, `libnfs_rejected_reply`, `libnfs_rpc_reply_body`, `libnfs_rpc_msg`, `libnfs_zdr_callmsg`, and `libnfs_zdr_replymsg`.

Authentication helpers are `authnone_create`, `libnfs_authunix_create`, `libnfs_authunix_create_default`, `libnfs_auth_destroy`, and the Kerberos-gated `libnfs_authgss_init` and `libnfs_authgss_gen_creds`. The global `_null_auth` is the default empty verifier.

## Control Flow

Primitive encode/decode functions advance `zdrs->pos` through `zdrs->buf` in network byte order. Fixed-width integers check buffer bounds before reading or writing. Variable data first encodes or decodes a 32-bit length, validates a hard 1 GiB clamp, copies or points into the stream buffer, and pads to the next 4-byte XDR boundary. Strings decode in place when the receive buffer already has a trailing NUL byte; otherwise they allocate stream-owned space and append the terminator. Arrays decode by allocating `count * element_size` from `zdr_malloc` after checking multiplication overflow and then invoking the generated element codec for each element.

RPC message processing starts with `libnfs_rpc_msg`, which decodes or encodes the XID and direction, then dispatches to call-body or reply-body helpers. Call bodies marshal RPC version, program, version, procedure, credential, and verifier. Reply bodies dispatch between accepted and denied replies. Accepted replies decode the verifier, accepted status, optional program mismatch bounds, and, for success, invoke the PDU-specific result decode callback.

With `HAVE_LIBKRB5`, verifier and accepted-reply handling add RPCSEC_GSS behavior. Encoding an AUTH_GSS verifier may compute a MIC over bytes already in the ZDR stream. Decoding `krb5p` accepted replies unwraps the protected payload into a GSS output buffer and temporarily repoints the ZDR stream to decrypted data. Decoding `krb5i` skips integrity prefix fields but leaves signature verification as a TODO.

## State and Persistence Behavior

`ZDR` objects are caller-owned, but decode allocations made through `zdr_malloc` are owned by the stream and live until `libnfs_zdr_destroy`. Decode results that point directly into `zdrs->buf` are valid only while the underlying RPC receive buffer remains valid. AUTH objects own `oa_base` buffers for credentials and verifiers and are freed by `libnfs_auth_destroy`. AUTH_UNIX credential data includes a timestamp from `rpc_current_time`, the selected uid/gid, the host string, and up to 16 auxiliary groups.

The implementation keeps no durable filesystem state. Kerberos paths mutate `rpc_context` fields such as GSS sequence number, context handle, credential flavor, and auth data, so the ZDR code participates in transport-session state but does not independently persist it.

## Dependencies and Integration Points

The file integrates with generated raw protocol codecs from `libnfs-raw*.h`, PDU allocation and processing in `pdu.c`, RPC context error reporting in `init.c`, Kerberos helpers in `krb5-wrapper.c`, and the high-level connection setup in `libnfs.c`. It depends on endian conversion (`htonl`, `ntohl`), process credentials (`getuid`, `getgid` where available), and GSSAPI functions when Kerberos is enabled.

## Risks and Edge Cases

The code performs many unaligned casts into `char *` buffers; the `(void *)` casts suppress aliasing warnings but may still rely on architectures tolerating unaligned access. Bounds checks are stronger for integers and bytes than for `libnfs_zdr_opaque`, which assumes callers have already sized the buffer correctly. `libnfs_zdr_string` accepts `maxsize` but does not enforce it directly. `libnfs_zdr_array` rejects multiplication overflow but not a protocol count greater than the caller-provided `maxsize`. `libnfs_zdr_pointer` encodes presence based on the existing pointer value and decodes absent pointers by overwriting `*objp` with `NULL`.

Memory ownership is subtle: bytes and strings may either alias the receive buffer or point to stream-owned allocations, while higher-level callbacks sometimes steal or deep-copy decoded data. RPCSEC_GSS integrity verification is incomplete for `krb5i`, and protected reply decoding repoints the stream buffer, so downstream decode logic must not assume the original buffer pointer remains active. AUTH creation has limited allocation-error checking after allocating nested credential buffers.

## Test Signals

Unit tests should round-trip all primitive codecs across encode and decode, including 4-byte padding, zero-length bytes, strings with and without in-buffer NUL terminators, pointer presence, arrays, vectors, and overflow/size-limit failures. RPC envelope tests should decode accepted success, program mismatch, denied RPC mismatch, and auth error replies. Security-focused tests should cover AUTH_UNIX group-count rejection above 16, allocation failures in auth creation, malformed lengths near 1 GiB, truncated buffers at every field boundary, and Kerberos-enabled builds for MIC, unwrap, and error paths. Integration tests are successful NFSv3/NFSv4 RPC calls through `pdu.c` using this ZDR backend.
