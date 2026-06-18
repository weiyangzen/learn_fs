<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_xids_to_sids.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_xids_to_sids.c

## Purpose
This file implements the asynchronous external `WINBINDD_XIDS_TO_SIDS` command. It maps newline-separated Unix ID requests to SID strings.

## Important APIs, Types, And Functions
The command is implemented by `winbindd_xids_to_sids_send()`, `winbindd_xids_to_sids_done()`, and `winbindd_xids_to_sids_recv()`. It uses `parse_xidlist()` from `winbindd_util.c`, `wb_xids2sids_send/recv()`, `struct unixid`, and `struct dom_sid`.

## Control Flow
`send()` validates null-terminated extra data, parses `U<id>` and `G<id>` lines, and starts the idmap conversion request. The callback receives an array of SIDs. `recv()` writes one line per input XID, using the SID string when mapped and `-` when the result is the null SID.

## State And Persistence Behavior
State is request-local: parsed XIDs, count, and result SIDs. Persistence is delegated to idmap backends, which may read or allocate mappings.

## Dependencies And Integration Points
It depends on winbind request framing, tevent, ID parsing utilities, idmap conversion helpers, and SID formatting. It integrates with clients that batch UID/GID-to-SID conversion.

## Risks And Test Signals
Risks include strict parser rejection, unsigned ID overflow, null SID handling, and response size accounting. Tests should cover UID and GID inputs, invalid type prefixes, empty input, unmapped IDs, and large batches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_xids_to_sids.c -->
