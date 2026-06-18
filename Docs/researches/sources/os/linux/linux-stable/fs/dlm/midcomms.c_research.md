# File Research: sources/os/linux/linux-stable/fs/dlm/midcomms.c

## Purpose
`midcomms.c` implements DLM’s mid-level communication reliability layer above lowcomms sockets. For protocol 3.2 peers it adds sequence numbers, ACKs, retransmission of unacknowledged messages, version detection, and a DLM-level FIN handshake.

## Core State
`struct midcomms_node` tracks per-node state:
- protocol version
- send and receive sequence counters
- unacknowledged send queue
- delivered-message ACK thresholds
- close/stop flags
- shutdown waitqueue
- reduced TCP-like termination state
- lockspace user count
- debugfs state

Nodes are stored in `node_hash[CONN_HASH_SIZE]` under SRCU.

`struct dlm_mhandle` wraps a lowcomms message and, for protocol 3.2, records the `struct dlm_opts` outer header, inner packet pointer, sequence number, ACK callback, and send-queue linkage.

## Version Detection
Version is inferred from early RCOM traffic:
- 3.1 messages are processed without the reliable wrapper.
- 3.2 messages use `DLM_OPTS` wrappers, ACKs, retransmit queues, and FIN messages.

The code treats RCOM status/names traffic specially because those recovery messages have their own retransmission behavior and are used for compatibility/version setup.

## Receive Path
`dlm_validate_incoming_buffer()` validates outer message lengths and returns the number of complete bytes available.

`dlm_process_incoming_buffer()` walks complete messages and dispatches by protocol version:
- `dlm_midcomms_receive_buffer_3_1()`
- `dlm_midcomms_receive_buffer_3_2()`

For 3.2:
- `DLM_OPTS` extracts the inner message and sequence.
- Expected sequence numbers are delivered to `dlm_receive_buffer()`.
- Duplicate/old sequence numbers are ACKed again.
- Unexpected future sequence numbers are ignored and logged.
- `DLM_ACK` removes acked messages from the send queue.
- `DLM_FIN` drives termination state.

## Send Path
`dlm_midcomms_get_mhandle()` allocates a message handle. For 3.2, it reserves `DLM_MIDCOMMS_OPT_LEN`, inserts the handle into the send queue, assigns a sequence, and returns the inner payload pointer.

`dlm_midcomms_commit_mhandle()` commits through lowcomms. For 3.2, it sets `o_nextcmd`, marks the handle committed, emits tracepoints, and relies on ACK processing to delete the mhandle.

`dlm_midcomms_unack_msg_resend()` walks committed unacknowledged messages and asks lowcomms to duplicate them after socket errors/reconnects.

## Termination
The file implements a DLM-level four-way FIN/ACK shutdown state machine using states:
- `DLM_CLOSED`
- `DLM_ESTABLISHED`
- `DLM_FIN_WAIT1`
- `DLM_FIN_WAIT2`
- `DLM_CLOSE_WAIT`
- `DLM_LAST_ACK`
- `DLM_CLOSING`

This is needed because SCTP lacks TCP-style half-close semantics and because lowcomms supports `othercon` compatibility sockets.

## Membership Integration
- `dlm_midcomms_add_member()` increments node use and moves closed nodes to established state.
- `dlm_midcomms_remove_member()` decrements use and can trigger passive FIN when the node is no longer used.
- `dlm_midcomms_shutdown()` actively shuts down all nodes, calls lowcomms shutdown, then resets node state.
- `dlm_midcomms_close()` aborts waiters, closes lowcomms state, removes debugfs/node hash entries, flushes queued messages, and defers freeing.

## Debug Raw Message Path
`dlm_midcomms_rawmsg_send()` lets debugfs send a raw DLM message through lowcomms. `midcomms_new_rawmsg_cb()` may fill a missing sequence number for wrapped messages.

## Risks and Notes
This file is protocol-sensitive. Known issues are documented in comments: unaligned message payloads, limited version-detection compatibility, incomplete tail-size validation for some payloads, and future fencing hooks for bad sequence behavior/timeouts.
