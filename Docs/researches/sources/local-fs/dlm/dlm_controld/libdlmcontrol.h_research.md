# File Research: sources/local-fs/dlm/dlm_controld/libdlmcontrol.h

This header is the public API contract for `libdlmcontrol`. It exposes dump, status, lockspace/node query, filesystem notification, fencing acknowledgement, and distributed run-command interfaces.

Key declarations:
- `DLMC_DUMP_SIZE` defines 1 MiB client dump buffers.
- Node flags include membership/start/disallowed/fencing/check-fs state bits.
- `struct dlmc_node` reports node id, flags, add/remove sequence numbers, fail reason, and fail timestamps.
- `struct dlmc_change` captures lockspace change state: member/join/remove/fail counts, wait condition/message state, sequence, and combined sequence.
- `struct dlmc_lockspace` exposes previous and next changes, lockspace flags, global id, and name.
- `DLMC_NODES_ALL`, `DLMC_NODES_MEMBERS`, and `DLMC_NODES_NEXT` define `dlmc_lockspace_nodes()` views.
- `DLMC_STATUS_VERBOSE` selects verbose status formatting.
- Filesystem result types are `DLMC_RESULT_REGISTER` and `DLMC_RESULT_NOTIFIED`.
- Run-command constants define UUID/command lengths, start behavior flags, check behavior flags, and status bits.

Important dependencies:
- The header uses `uint32_t`, `uint64_t`, and `DLM_LOCKSPACE_LEN`, so consumers need integer typedefs and DLM constants available through include ordering or surrounding package headers.
- Function implementations live in `lib.c`; daemon-side protocol handling lives in `main.c`.

Notable details:
- The comments document lockspace node views carefully, especially the difference between completed and in-progress change groups.
- Run-command semantics are cluster-wide: one node requests command execution, each daemon helper executes locally when selected, and the originator collects replies.
