# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_dmsg.c

## Purpose

Implements the kernel DMSG messaging layer used for stateful message transactions over a file-backed communication endpoint such as a socket or pipe. It manages IO threads, message framing, transaction state trees, parent/child circuit topology, automatic link messages, abort/failure simulation, and message allocation/freeing.

## Key Responsibilities

- Initializes and reconnects `kdmsg_iocom_t` communication sessions.
- Runs one read thread and one write thread per iocom.
- Reads/writes DMSG headers and aligned auxiliary payloads through `fp_read()` / `fp_write()`.
- Tracks persistent message transactions in red-black trees by message ID.
- Tracks nested/circuit transactions through parent `subq` queues.
- Handles CREATE/DELETE/REPLY/ABORT protocol state transitions.
- Provides automatic handling for link-level `LNK_CONN`, `LNK_SPAN`, and `LNK_PING` messages.
- Simulates transaction failures on link loss so upper layers get cleanup callbacks.
- Computes header and auxiliary CRCs before transmit.
- Exposes `kdmsg.debug` sysctl.

## Main Data Structures and State

- `kdmsg_iocom_t`: owns locks, file pointer, message queue, state trees, IO threads, auto link fields, sequence number, flags, and callbacks.
- `kdmsg_state_t`: represents a persistent transaction, with `rxcmd`, `txcmd`, `icmd`, `msgid`, parent/subq topology, refs, flags, callback, and private data.
- `kdmsg_msg_t`: carries a DMSG header union, optional aux data, transaction state pointer, and queue linkage.
- `staterd_tree`: received command transactions.
- `statewr_tree`: locally initiated outbound transactions.
- `state0`: root state for one-off messages and top-level transactions.
- `freerd_state` / `freewr_state`: cached state objects used by receive/transmit paths.

## Initialization and Connection Flow

- `kdmsg_iocom_init()` zeroes and initializes an iocom, message lock, queue, state trees, root state, allocator type, callback, and flags.
- `kdmsg_iocom_reconnect()` stops existing IO threads, drops the old file, installs a new file pointer, resets sequencing/control flags, and creates read/write threads.
- `kdmsg_iocom_autoinitiate()` sends an automatic `DMSG_LNK_CONN | DMSGF_CREATE` and optionally stores the resulting connection state.

## IO Threads

- `kdmsg_iocom_thread_rd()`:
  - Reads fixed header, validates magic and header size.
  - Allocates a message based on base command.
  - Reads extended header and aligned auxiliary data.
  - Checks payload size against `DMSG_AUX_MAX`.
  - Passes the message to `kdmsg_msg_receive_handling()`.
  - On error/shutdown, shuts down the file and signals TX termination.

- `kdmsg_iocom_thread_wr()`:
  - Sleeps while the transmit queue is empty.
  - Dequeues messages and runs `kdmsg_state_msgtx()`.
  - Writes header and optional aux payload.
  - Calls `kdmsg_state_cleanuptx()` even on write failure after state transition.
  - On termination, waits for RX to exit, drains queued messages, simulates failures, and waits for all states to disappear before exit.

## Receive State Machine

- `kdmsg_msg_receive_handling()` runs state lookup/update via `kdmsg_state_msgrx()`, then dispatches to:
  - `msg->state->func` if the state has a callback.
  - `kdmsg_autorxmsg()` when automatic link handling is enabled.
  - `iocom->rcvmsg()` otherwise.
- `kdmsg_state_msgrx()`:
  - Looks up state by message ID in read or write tree depending on `DMSGF_REVTRANS`.
  - Handles one-off messages without CREATE/DELETE/ABORT.
  - Creates new state for received transaction CREATE messages.
  - Validates DELETE, REPLY|CREATE, REPLY|DELETE, and ABORT races.
  - Removes fully closed states from RB trees after both RX and TX sides are deleted.
  - Computes `msg->tcmd` for higher-level switch dispatch.

## Transmit State Machine

- `kdmsg_state_msgtx()`:
  - Validates CREATE/DELETE/REPLY/ABORT combinations before transmit.
  - Initializes outbound transaction state on CREATE.
  - Detects already-closed or reused states and returns `EALREADY` for harmless raced abort/delete cases.
  - Sets `KDMSG_STATE_INTERLOCK` while a send may block, preventing receive-side races.
- `kdmsg_state_cleanuptx()`:
  - Clears interlock and wakes any waiters.
  - Marks TX DELETE.
  - Removes fully closed states from the appropriate RB tree.
  - Removes leaf subq topology when possible.
  - Executes deferred aborts if a state became dying/aborting during send.

## Failure and Abort Handling

- `kdmsg_drain_msgq()` drains queued TX messages during shutdown.
- `kdmsg_drain_msg()` simulates send-side processing and link failure for a message’s state.
- `kdmsg_simulate_failure()` recursively walks a state’s subtransactions and calls `kdmsg_state_abort()`.
- `kdmsg_state_abort()` marks a state aborting/dying and synthesizes a received `DMSG_LNK_ERROR` DELETE message if RX is not already closed.
- `kdmsg_state_dying()` recursively prevents new transmissions on a state and its children.
- `kdmsg_subq_delete()` unlinks a state from its parent queue and drops parent/subq references.

## Message API

- `kdmsg_msg_alloc()` allocates messages and, for outbound CREATE commands, allocates/inserts a new transaction state with a msgid derived from the state pointer.
- `kdmsg_msg_free()` releases aux data, drops state reference, and frees message memory.
- `kdmsg_detach_aux_data()` transfers aux buffer ownership to `kdmsg_data_t`.
- `kdmsg_free_aux_data()` frees detached aux buffers.
- `kdmsg_msg_write()` / `kdmsg_msg_write_locked()` compute CRCs, assign sequence salt, set msgid/circuit fields, and queue or drain messages.
- `kdmsg_msg_reply()` / `kdmsg_msg_result()` reply to a message with a `DMSG_LNK_ERROR` result, either terminating or continuing the transaction.
- `kdmsg_state_reply()` / `kdmsg_state_result()` do the same from a held state.

## Automatic Link Handling

- `kdmsg_lnk_conn_reply()` reacts to `LNK_CONN` acknowledgements and can automatically start `LNK_SPAN`.
- `kdmsg_lnk_span_reply()` handles span callbacks and termination.
- `kdmsg_autorxmsg()` automatically replies to pings, acknowledges/maintains/terminates auto connection and span transactions, and delegates unhandled messages to `iocom->rcvmsg()`.

## Filesystem/Storage Relevance

DMSG is not a local filesystem implementation itself, but it is relevant to DragonFlyBSD storage/filesystem infrastructure because it provides a stateful kernel messaging substrate used by higher-level distributed/block/filesystem components. Its transaction/circuit semantics are suitable for asynchronous storage protocol operations that need explicit create/delete lifecycle and link-loss cleanup.

## Research Notes

- State lifetime is reference-counted and constrained by RB-tree insertion, parent subq insertion, message ownership, and cached free-state references.
- Link-loss handling is intentionally callback-driven: upper layers receive synthetic transaction termination messages to clean up asynchronous operations.
- The code has a visible typo/bug-like diagnostic path in `kdmsg_state_abort()` using `kdio_printf(iocom, ...)` where no local `iocom` variable is declared in that function body; macro expansion depends on a valid symbol and this would be suspicious in isolation.
- Protocol race handling treats many ABORT+DELETE races as `EALREADY` and discards them without failing the connection.
