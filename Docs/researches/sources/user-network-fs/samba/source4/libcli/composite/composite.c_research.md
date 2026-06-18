# sources/user-network-fs/samba/source4/libcli/composite/composite.c

Purpose: implements the small "composite" async helper layer used by older Samba4 client code to expose multi-step async operations as one context with a synchronous wait option. It allocates `struct composite_context`, tracks completion/error state, waits on a `tevent_context`, and wires continuations for nested composite, SMB1, SMB2, and NBT requests.

Important APIs: `composite_create()`, `composite_wait()`, `composite_wait_free()`, `composite_error()`, `composite_done()`, `composite_nomem()`, `composite_is_ok()`, `composite_continue()`, `composite_continue_smb()`, `composite_continue_smb2()`, and `composite_continue_nbt()`. `composite_trigger()` is an internal zero-time timer callback used when an operation completes before the caller has installed `async.fn`.

Control flow and state: callers allocate a context in `COMPOSITE_STATE_IN_PROGRESS`, attach continuation callbacks, and eventually call done or error. `composite_wait()` marks `used_wait` and repeatedly calls `tevent_loop_once()` until state reaches `COMPOSITE_STATE_DONE` or `COMPOSITE_STATE_ERROR`. The continuation helpers set child request callbacks and propagate immediate child failure to the parent.

State and persistence: state is entirely in-memory, talloc-owned, and event-loop driven. There is no disk persistence. The subtle persistent behavior is callback scheduling: if neither synchronous wait nor callback is active at completion time, the code schedules a zero-time timer under the context so the eventual caller can still receive notification.

Dependencies and integration: depends on tevent, talloc, NTSTATUS, SMB1 `smbcli_request`, SMB2 `smb2_request`, and NBT name requests. It is used by connection, resolver, and other older libcli APIs that predate `tevent_req`.

Risks: null `event_ctx` would make wait/trigger paths unsafe for callers that did not initialize correctly. Early completion behavior depends on the context staying alive until the zero-time timer fires. `composite_continue_smb*()` only detects requests already beyond receive state; later errors remain callback responsibility. Test signals include async operations that complete immediately, callback-after-completion cases, child request allocation failure, and `tevent_loop_once()` failure handling.
