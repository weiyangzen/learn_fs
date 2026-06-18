# File Research: sources/os/linux/linux/fs/dlm/midcomms.c

## Role

`midcomms.c` implements DLM’s reliable application-layer communication over lowcomms. It adds protocol version detection, sequence numbers, acknowledgements, retransmission, and a DLM-level FIN/ACK termination state machine.

## Node State

`struct midcomms_node` is keyed by nodeid in `node_hash`. It stores protocol version, send and receive sequence counters, an unbounded send queue of committed message handles, termination flags, delivered-message counters, a shutdown waitqueue, and a reduced TCP-like close state.

`struct dlm_mhandle` represents one outgoing midcomms message. For protocol 3.2, it is linked on the node send queue until acknowledged.

## Version Handling

Protocol version is detected from early RCOM traffic:
- 3.1 messages are passed through without reliable retransmission support.
- 3.2 messages use `DLM_OPTS` wrappers carrying sequence numbers and inner commands.

`dlm_midcomms_version_wait()` waits for all nodes to detect a version, close, or be force-closed.

## Reliable Delivery

For 3.2:
- Outgoing messages are wrapped in `struct dlm_opts`.
- `seq_send` is assigned when the lowcomms message buffer is allocated.
- Committed messages stay on `send_queue`.
- Receivers deliver only expected sequence numbers and ignore duplicates/out-of-order messages.
- `DLM_ACK` acknowledges all messages before the supplied sequence number.
- `dlm_midcomms_unack_msg_resend()` retransmits committed unacknowledged messages after lowcomms socket errors.

ACKs are sent opportunistically when delivered-message thresholds are exceeded and directly for FIN or duplicate sequence handling.

## Receive Path

`dlm_process_incoming_buffer()` walks complete lowcomms messages and dispatches based on header version.

`dlm_midcomms_receive_buffer_3_2()` validates `DLM_OPTS` lengths, checks supported inner commands, handles early RCOM version detection messages specially, processes ACKs, and routes reliable messages through `dlm_midcomms_receive_buffer()`.

3.1 receive handling only validates basic RCOM/message lengths and dispatches to `dlm_receive_buffer()`.

## Termination State Machine

The file implements reduced TCP-style states: closed, established, fin-wait-1, fin-wait-2, close-wait, last-ack, and closing.

`dlm_midcomms_shutdown()` performs active shutdown for all nodes, sends FIN for established 3.2 peers, waits for closed state or timeout, then calls lowcomms shutdown and resets nodes.

`dlm_midcomms_add_member()` and `dlm_midcomms_remove_member()` maintain a user count per node. When the count reaches zero, passive close handling may send FIN after receiving a peer FIN.

`dlm_midcomms_close()` force-closes a node, wakes shutdown waiters, removes the midcomms node, calls lowcomms close, flushes pending messages, and releases through SRCU.

## Raw Debug Send

`dlm_midcomms_rawmsg_send()` sends a user-provided raw DLM message for debug use and can fill a missing sequence in a raw `DLM_OPTS` message.

## Important Behaviors and Invariants

- For 3.2, committed messages must remain queued until acknowledged.
- SRCU lifetime protects node lookup while callers allocate and commit mhandles.
- ACK processing may release message handles, so commit holds RCU read-side protection while committing.
- STOP_TX/STOP_RX flags guard sends/receives during DLM-level shutdown.
- The close mutex serializes force close with stop/remove paths.

## Research Notes

Read completely. This file is the reliability layer between byte-stream transport and DLM lock/recovery message processing.
