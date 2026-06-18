# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmast.c

## Purpose
Implements OCFS2 DLM AST and BAST handling for local and remote locks. ASTs notify lock grant/conversion completion; BASTs notify that a granted lock blocks another request and should be downconverted.

## AST/BAST Queueing
`__dlm_queue_ast()` and `__dlm_queue_bast()` place locks on DLM pending AST/BAST lists under `dlm->ast_lock`, taking an extra lock reference while queued. Public `dlm_queue_ast()` wraps the AST queue path with locking.

`dlm_should_cancel_bast()` suppresses obsolete BASTs when an AST changes a lock mode so it no longer blocks the highest blocked mode. For example, a lock downconverted to NL no longer needs a BAST.

## LVB Handling
`dlm_update_lvb()` updates lock value block state when this node owns the lock resource:
- GET requests copy the resource LVB into the lockstatus block.
- PUT requests are intentionally not applied here because downconvert paths should already apply them in place.
- GET/PUT flags are cleared afterward.

## Local AST/BAST Execution
`dlm_do_local_ast()`:
- verifies the lock is local
- updates LVB state
- invokes the lock’s AST callback with `astdata`.

`dlm_do_local_bast()`:
- verifies local ownership
- invokes the BAST callback with `astdata` and blocked mode.

These callbacks are expected to be callable in the DLM execution context.

## Remote AST Execution
`dlm_do_remote_ast()` updates LVB state and sends a proxy AST to the remote lock holder via `dlm_send_proxy_ast()`.

`dlm_send_proxy_ast_msg()` constructs `struct dlm_proxy_ast`, optionally appends LVB data for GET_LVB, and sends it over `o2net_send_message_vec()` with message type `DLM_PROXY_AST_MSG`. It treats `DLM_RECOVERING` and `DLM_MIGRATING` responses as fatal inconsistencies.

## Proxy AST Handler
`dlm_proxy_ast_handler()` receives proxy AST/BAST messages from the lock resource master. It:
- grabs the DLM context.
- validates domain join state, name length, LVB flags, and AST type.
- looks up the lock resource.
- rejects recovery/migration states with `DLM_RECOVERING` or `DLM_MIGRATING`.
- finds the target lock in converting/blocked/granted lists depending on AST type.
- for AST, moves the lock to granted, applies convert mode, sets `lksb->status`, and copies incoming LVB if requested.
- drops the resource lock and invokes local AST or BAST callback.

Unknown lock/resource cases generally return `DLM_IVLOCKID` or `DLM_NORMAL` depending on whether the condition can be safely ignored.

## Important Dependencies
- O2CB TCP transport for proxy messaging.
- DLM lock-resource list discipline and reference counting.
- DLM recovery/migration state flags.
- LVB flags from `dlmapi.h`.
