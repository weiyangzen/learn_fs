<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_sids_to_xids.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_sids_to_xids.c

## Purpose
This file implements the asynchronous external `WINBINDD_SIDS_TO_XIDS` command. It maps a newline-separated list of SID strings to Unix IDs and formats a line-aligned response for clients.

## Important APIs, Types, And Functions
The command is implemented by `winbindd_sids_to_xids_send()`, callback `winbindd_sids_to_xids_done()`, and `winbindd_sids_to_xids_recv()`. It uses `parse_sidlist()` from `winbindd_util.c`, `wb_sids2xids_send/recv()`, `struct dom_sid`, and `struct unixid`.

## Control Flow
`send()` validates that extra data is either empty or null-terminated, parses the SID list, and dispatches `wb_sids2xids_send()`. The callback allocates an output `unixid` array sized to the input SID count and receives mapping results. `recv()` turns each mapped ID into `U<id>`, `G<id>`, or `B<id>` lines and emits a blank line for unmapped or invalid entries.

## State And Persistence Behavior
State is request-local: parsed SIDs, count, and mapped XIDs. Persistence is delegated to the idmap layer, which may read or allocate mappings according to its backend policy.

## Dependencies And Integration Points
It depends on winbind request framing, tevent, SID parsing, idmap conversion helpers, and `response->extra_data`. It integrates with clients that batch SID-to-UID/GID conversions and expect line order to match input order.

## Risks And Test Signals
Risks include malformed non-null-terminated client payloads, very large SID lists, `UINT32_MAX` being treated as unmapped, and exact response length accounting through `talloc_get_size()`. Test signals are batch mappings containing UID, GID, BOTH, unmapped, empty input, and invalid SID syntax.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_sids_to_xids.c -->
