# sources/security-integrity/audit-userspace/src/auditd-dispatch.c

## Purpose
`auditd-dispatch.c` is the thin adapter between auditd events and the audisp dispatcher library. It initializes, shuts down, reconfigures, and queues events for plugins.

## Important APIs, Types, And Functions
Public functions are `init_dispatcher`, `shutdown_dispatcher`, `reconfigure_dispatcher`, and `dispatch_event`. `dispatch_event` allocates an `event_t`, fills `audit_dispatcher_header` fields, copies event bytes according to protocol version, and calls `libdisp_enqueue`.

## Control Flow
Startup calls `libdisp_init(config)`. Shutdown calls `libdisp_shutdown`. Reconfiguration calls `libdisp_reconfigure(config)`. For each routed audit event, `dispatch_event` first returns success if the dispatcher is inactive, then allocates an event, sets version/header/type/size, copies either `rep->msg.data` for protocol v1 or `rep->message` for protocol v2, rejects unknown protocol versions, and lets libdisp own the queue item.

## State And Persistence
This file keeps no persistent local state. Dispatcher state lives in libdisp and is reached through its API. Each queued event allocation is transient and handed to the dispatcher queue.

## Dependencies And Integration
It depends on `libaudit`, `private.h`, `auditd-dispatch.h`, and `libdisp.h`. It is called from `auditd.c` via `distribute_event` and from `auditd-reconfigure.c` after config changes.

## Risks
The critical risk is copy sizing: `event_t->data` must be large enough for `rep->msg.nlh.nlmsg_len` or `rep->len`. Protocol choice is tied to whether auditd has formatted a message as enriched/node-tagged. If callers pass inconsistent length/message fields, plugins may receive truncated or malformed data.

## Test Signals
Existing `format_event_test` links this file indirectly through auditd event formatting. Focused unit tests could stub libdisp to assert inactive behavior, protocol rejection, v1/v2 size fields, allocation failure, and overflow return propagation.
