# sources/user-network-fs/samba/source4/libcli/composite/composite.h

Purpose: public interface for Samba4 composite requests, a legacy async abstraction for representing a multi-step client operation as one stateful request object.

Important types and APIs: defines `enum composite_state` with init, in-progress, done, and error states; defines `struct composite_context` with externally visible `state`, implementation `private_data`, final `NTSTATUS`, `event_ctx`, async callback, and `used_wait`; declares creation, wait/free, completion/error, memory/status helpers, and continuation attachment for composite, SMB1, SMB2, and NBT child operations.

Control flow contract: a producer creates a context, stores operation-private state in `private_data`, starts child async work, and calls `composite_done()` or `composite_error()`. A consumer either installs `async.fn` or calls `composite_wait()`/`composite_wait_free()`.

State and persistence: all state is volatile and talloc-managed. The header exposes enough structure for callers to inspect state and install callbacks directly, so ABI/API stability matters.

Dependencies and integration: includes raw SMB interfaces and forward declares tevent, SMB1, SMB2, and NBT request types. It is included by libcli connection and resolver paths that bridge older composite callbacks with newer modules.

Risks: because fields are public, callers can mutate state incorrectly. The enum ordering is semantically important because wait loops compare state numerically against `COMPOSITE_STATE_DONE`. Test signals should cover direct field use, callback registration, and failure propagation from each continuation helper.
