# File Research: sources/local-fs/dlm/dlm_controld/daemon_cpg.c

## Purpose
Implements the daemon-wide Corosync CPG group `dlm:controld`. It coordinates cluster-wide protocol negotiation, fencing, startup safety, stateful merge handling, distributed helper-run requests, message encoding, and daemon status export.

## Main Behavior
- Defines DLM daemon protocol structures for maximum supported daemon/kernel protocol and selected runtime daemon/kernel protocol.
- Provides common CPG message send and header conversion helpers used by both daemon-wide and per-lockspace CPG code.
- Validates incoming message sender nodeid and daemon protocol major/minor compatibility.
- Tracks daemon members in `node_daemon`, including membership state, clean protocol state, stateful merge flag, fencing state, fence actor candidates, fence agent pid, timestamps, and per-node fence config.
- Maintains `fence_in_progress_unknown` (FIPU) so newly joined nodes do not start lockspaces while previous members may still be fencing failed nodes.
- Fencing work loop:
  - Waits for daemon and cluster ring IDs to match.
  - Optionally waits for quorum.
  - Detects stateful merges and kills/defers merged members based on quorum/two-node rules.
  - Handles startup fencing by moving startup nodes into normal `need_fencing` state after delay.
  - Selects the lowest surviving fence actor from nodes present when failure was observed.
  - Runs fence agents through `fence_request()` and checks completion through `fence_result()`.
  - Supports serial or concurrent fencing based on options.
  - Uses parallel-priority fence config sequencing: next parallel device on success, next priority device on failure.
  - Broadcasts `DLM_MSG_FENCE_RESULT` and `DLM_MSG_FENCE_CLEAR`.
  - Clears FIPU through startup fencing completion, explicit clears from prior members, or all-members-FIPU detection when startup fencing is disabled.
- Protocol negotiation:
  - On daemon CPG join, all nodes send max/run protocol data.
  - Once all protocol messages are present, the daemon proposes minimum compatible versions.
  - Nodes adopt nonzero run protocol from a peer or their own proposal.
  - `set_protocol_stateful()` marks the local daemon as stateful after lockspace recovery begins, making later partition merges detectable.
- Distributed run support:
  - Receives and sends `DLM_MSG_RUN_REQUEST`/`DLM_MSG_RUN_REPLY`.
  - Tracks replies only on the starting node.
  - Dispatches accepted commands to the helper process through `send_helper_run_request()`.
  - Supports start-node participation flags and destination-node targeting.
- CPG callbacks:
  - `confchg_cb_daemon()` records member/join/remove lists, sends protocol on joins, marks failed members for recovery/fencing, and sets clear flags for joining nodes.
  - `totem_cb_daemon()` stores daemon ring id and reruns fencing work.
  - `deliver_cb_daemon()` dispatches protocol, fence, clear, and run messages.
- Lifecycle:
  - `setup_cpg_daemon()` initializes protocol maxima, joins `dlm:controld`, and returns its CPG fd.
  - `close_cpg_daemon()` leaves/finalizes daemon and lockspace CPGs, stopping kernel lockspaces first.
  - `send_state_daemon*()` exports daemon, daemon-node, and startup-node textual state records.

## Integration Points
- Called by the main daemon event loop for daemon CPG dispatch.
- Supplies message helpers to `cpg.c`, `plock.c`, `deadlock.c`, and run-helper code.
- Uses fencing primitives from `fence.c` and fence config from `fence_config.c`.
- Uses cluster state globals maintained by membership/quorum code outside this file.
- Kicks nodes from Corosync through `kick_node_from_cluster()` when safety requires it.

## Risks and Notes
- Fencing correctness is central: lockspaces can remain blocked while FIPU, startup nodes, or `need_fencing` are unresolved.
- Stateful merge handling is conservative and may intentionally kill peer cluster membership to avoid using stale DLM state.
- Some send helpers pre-convert fields manually and call `_send_message()` directly rather than `dlm_send_message_daemon()`.
- Run-command payloads are trusted only after helper-level command allowlisting.
