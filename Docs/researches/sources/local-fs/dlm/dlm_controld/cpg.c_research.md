# File Research: sources/local-fs/dlm/dlm_controld/cpg.c

## Purpose
Implements per-lockspace Corosync CPG membership control. It translates CPG membership changes into safe DLM kernel stop/reconfigure/start cycles, synchronizes start barriers between lockspace members, coordinates plock state transfer, and exposes lockspace/node status to the control API.

## Main Behavior
- Maintains per-lockspace `change` records for CPG confchg events and `node_history` records for node add/remove/failure/fencing/fs-notify state.
- On a lockspace membership change:
  - Record member, joined, removed, and failed node sets.
  - Stop kernel lock activity through sysfs `control=0`.
  - Mark failed nodes as needing fencing when fencing is enabled and the node had previously sent a valid start.
  - Purge plock state for removed nodes.
  - Wait for required conditions: matching Corosync/quorum ring IDs, quorum if enabled, fencing completion, and fs notification acknowledgements.
  - Send a `DLM_MSG_START` message containing full change details.
  - Wait for all members' start messages as an agreed barrier.
  - Update configfs lockspace members, set lockspace id/nodir when joining, and restart kernel locking via `control=1`.
  - Finish initial kernel join by writing sysfs `event_done`.
- Uses detailed change matching in received start/plock-done messages. Matching checks sender membership, node add times, counts, member IDs, NACK flags, and duplicate/old change patterns.
- Sends NACK start messages for older identical changes so peers do not accidentally match stale messages.
- Coordinates plock handoff:
  - New joiners set `need_plocks`.
  - The lowest member reporting plock state becomes the data node.
  - New nodes ignore/suspend plock messages until saved state is ready, then replay saved messages after `DLM_MSG_PLOCKS_DONE`.
  - The data node sends all plock state when nodes have been added.
- Handles `DLM_MSG_RELEASE_RECOVER` on leave, allowing the initiator's release-recovery option to be written to configfs before member removal.
- Joins lockspace CPG groups named `dlm:ls:<lockspace>`, deriving a global id from the CPG name CRC.
- Leaves lockspace CPGs on kernel offline events, finalizes CPG handles after the leave callback, purges local plocks, and frees lockspace state.
- Exposes `set_lockspace_info()`, `set_node_info()`, `set_lockspaces()`, and `set_lockspace_nodes()` for `libdlmcontrol` queries.

## Integration Points
- Uses sysfs/configfs functions from `action.c`.
- Uses cluster membership and fencing state from `member.c`/`daemon_cpg.c`.
- Dispatches plock messages to `plock.c` and receives plock state completion callbacks.
- Uses message send, header conversion, message validation, and protocol-state transitions from `daemon_cpg.c`.
- Called by the main daemon event loop via CPG client callbacks.

## Risks and Notes
- Correctness relies on Corosync CPG's ordered delivery and identical confchg sequence across members.
- The code deliberately waits for CPG and cluster ring IDs to match to avoid acting on inconsistent membership views.
- Fencing and fs-notify waits can hold a lockspace stopped until external conditions complete.
- Deadlock message handling is present only under inactive `#if 0` blocks in this file, so the active daemon does not dispatch deadlock messages from lockspace CPG.
- Many status/debug fields are maintained specifically for control-socket diagnostics.
