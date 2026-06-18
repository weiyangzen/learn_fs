# sources/user-network-fs/samba/source4/nbt_server/irpc.c

## Purpose

`irpc.c` exposes internal RPC services from the NBT server. It provides statistics and a get-DC helper used by other Samba components that need port-138 Netlogon replies to be received by the NBT server process.

## Important APIs, Types, and Functions

`nbtd_information()` returns `NBTD_INFO_STATISTICS`. `struct getdc_state` tracks deferred get-DC replies. `nbtd_getdcname()` sends a Netlogon SAM_LOGON request and defers the IRPC response. `getdc_recv_netlogon_reply()` parses the mailslot response and completes the IRPC call. `nbtd_register_irpc()` registers NBTD information, getdcname, and WINS proxy handlers.

## Control Flow

For getdc, the handler selects an outgoing interface for the requested IP, creates a temporary mailslot, builds a version-1 `LOGON_SAM_LOGON_REQUEST`, sends it to `<domain>[0x1c]` at UDP port 138, marks the IRPC message deferred, and returns. The temporary mailslot callback parses the Netlogon response, validates version, strips leading backslashes from the PDC name, stores `out.dcname`, and sends the deferred IRPC reply.

## State and Persistence Behavior

The server statistics pointer is returned directly from `nbtd_server`. Getdc state is temporary and talloc-owned by the IRPC message. The function does not persist data but relies on the NBT server's live datagram socket.

## Dependencies and Integration Points

Dependencies include Samba messaging/IRPC, generated `ndr_irpc` definitions, libdgram Netlogon helpers, NBT name construction, socket address creation, and WINS proxy functions. Winbind is the motivating consumer mentioned in comments.

## Risks and Test Signals

Risks include no explicit timeout handling shown for deferred getdc, temporary mailslot lifetime coupling, accepting only Netlogon NT version 1, source interface selection errors, and debug message wording referring to ntlogon parse. Tests should query statistics, perform getdc against responsive and non-responsive DCs, validate malformed replies, verify deferred reply completion, and exercise WINS proxy registration failures.
