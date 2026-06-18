<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/libcliraw.h -->
# sources/user-network-fs/samba/source4/libcli/raw/libcliraw.h

Purpose: `libcliraw.h` is the public/internal umbrella header for source4 raw SMB client operations. It combines raw interface data structures with transport/session/tree/request state and declares the send/recv/sync entry points used by higher-level client, composite, torture, and NTVFS code.

Important APIs, types, and functions: The main state structs are `smbcli_negotiate`, `smbcli_socket`, `smbcli_options`, `smbcli_transport`, `smbcli_session`, `smbcli_tree`, and `smbcli_request`. `smbcli_request_state` tracks request lifecycle. The header exposes request helpers such as `smbcli_request_destroy`, `smbcli_request_simple_recv`, `smbcli_transport_process`, raw operations for open/close/read/write/lock/seek/rename/mkdir/unlink/chkpath/flush, metadata calls (`smb_raw_fileinfo`, `smb_raw_pathinfo`, `smb_raw_fsinfo`, `smb_raw_setfsinfo`), trans2 helpers, change notify, echo, tree/session teardown, oplock handlers, idle handlers, and raw search entry points. `SMBCLI_CHECK_WCT` and `SMBCLI_CHECK_MIN_WCT` are parser guard macros.

Control flow: Callers typically allocate or reuse a tree/session/transport, call a `*_send` function that returns an `smbcli_request`, then call a matching `*_recv` or use the sync wrapper. Request objects move from `INIT` through `RECV` to `DONE` or `ERROR`, with `smbcli_request_destroy` returning the final `NTSTATUS`. Parser functions use word-count macros to reject malformed replies and jump to a common cleanup label.

State and persistence behavior: The structs hold negotiated protocol state, server capabilities, security blobs, signing/options, event context, last transport error, oplock callback state, session IDs, tree IDs, request buffers, async callbacks, and trans2/nttrans substate. No filesystem data is persisted here; it is connection/request state with talloc-managed lifetimes.

Dependencies and integration points: This header includes `smb_common.h`, raw request buffer definitions, NBT NDR types, `interfaces.h`, and SMB2 negotiate-context types. It integrates with `smbXcli` transport/session/tree objects, tevent-driven request processing, client wrappers, composite operations, raw implementations, and torture tests.

Risks: This header exposes low-level internals, so misuse can bypass safer composite abstractions. Request lifetime is subtle because `do_not_free` can suppress cleanup and async callbacks can discard replies if unset. Buffer pointers in `smbcli_request` are invalidated by growth/reallocation. The macros assume a local `failed` label and mutate `req->status`, so they require consistent function structure.

Test signals: Raw torture suites exercise most declared operations. Transport tests should check negotiate state, timeout handling, request destruction status propagation, malformed WCT rejection, oplock callback paths, and async send/recv pairing. Build coverage is important because this header is included throughout raw client code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/libcliraw.h -->
