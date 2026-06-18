# sources/user-network-fs/samba/source3/libsmb/clidgram.c

## Purpose

`clidgram.c` implements NetBIOS datagram client support for a specific high-level operation: sending a mailslot-based NetLogon `GETDC` request and parsing the datagram response to discover a domain controller. It bridges Samba client code, nmbd datagram sending, local packet-reader sockets, and NDR-encoded NetLogon payloads.

## Important APIs, Types, and Functions

- `nbt_getdc_send()` starts the asynchronous GetDC request. It validates IPv4, builds a unique return mailslot, locates `nmbd`, prepares the datagram packet, opens a packet reader, and later sends the packet to nmbd.
- `nbt_getdc_recv()` returns the discovered `nt_version`, DC name, and optional `netlogon_samlogon_response`.
- `nbt_getdc()` is the synchronous wrapper with a private tevent context and timeout.
- `cli_prep_mailslot()` builds the NetBIOS datagram plus embedded SMB transaction mailslot payload.
- `prep_getdc_request()` NDR-encodes an `nbt_netlogon_packet` with `LOGON_SAM_LOGON_REQUEST`.
- `parse_getdc_response()` validates the datagram SMB wrapper, NDR-pulls the SMB transaction, parses the NetLogon SAM logon response, maps it to canonical form, validates the returned domain, and extracts the DC name.
- `struct nbt_getdc_state` keeps the async request context, messaging context, nmbd pid, return mailslot, target address/domain/SID/version, outbound packet, and parsed outputs.

## Control Flow

`nbt_getdc_send()` rejects non-IPv4 targets with `NT_STATUS_NOT_SUPPORTED`; the packet format stores an IPv4 address in `packet_struct.ip`. It builds `\\MAILSLOT\\NET\\GETDC...`-style state using `mailslot_name()`, reads nmbd's pidfile, randomizes a datagram id, and calls `prep_getdc_request()`. That helper fills a NetLogon SAM logon request using local NetBIOS name, account information, optional domain SID, requested NT version, and token fields, then passes the encoded blob to `cli_prep_mailslot()`.

`cli_prep_mailslot()` constructs a direct group or unique NetBIOS datagram with source and destination NBT names, lays out an SMB transaction mailslot body, enforces `MAX_DGRAM_SIZE`, copies the caller payload, sets `datasize`, stores destination IPv4 and timestamp, and emits debug diagnostics. After preparation, `nbt_getdc_send()` starts `nb_packet_reader_send()` against nmbd's local datagram socket directory and the private return mailslot.

When the reader is ready, `nbt_getdc_got_reader()` sends the packet to nmbd via `messaging_send_buf(MSG_SEND_PACKET)` and starts `nb_packet_read_send()`. `nbt_getdc_got_response()` receives one packet and calls `parse_getdc_response()`. A valid response completes the tevent request; parse failure maps to `NT_STATUS_INVALID_NETWORK_RESPONSE`.

## State and Persistence Behavior

The module does not persist data itself. It depends on nmbd's pidfile and local socket directory as runtime state. Request state is talloc-scoped to the tevent request; response objects are moved to the caller in `nbt_getdc_recv()`. `nbt_getdc()` uses a stackframe and frees it after polling. Datagram ids are random and masked to 15 bits.

## Dependencies and Integration Points

The file depends on `tevent`, Samba messaging, nmbd packet reader helpers, NetBIOS name/mailslot helpers, NDR-generated NetLogon and datagram parsers, `pull_netlogon_samlogon_response()`, Samba loadparm values such as `lp_netbios_name()`, `lp_pid_directory()`, and `global_nmbd_socket_dir()`, plus pidfile support. The public prototypes are declared in `clidgram.h`.

## Risks and Edge Cases

- IPv6 is unsupported even though the API accepts `sockaddr_storage`.
- The implementation requires a running local `nmbd`; absence of nmbd returns not-supported rather than trying direct UDP.
- `parse_getdc_response()` expects an SMB transaction datagram and validates returned domain equality; cross-domain or alias behavior may fail intentionally.
- Mailslot construction manipulates the SMB buffer by backing up four bytes for the TCP length convention. That area is protected by existing Samba packet layout assumptions and should be regression-tested if packet structures change.
- A single response is read. Retry, multi-response selection, and packet id correlation are delegated to surrounding behavior or not implemented here.

## Test Signals

Tests should cover no-nmbd behavior, IPv6 rejection, datagram size overflow, malformed datagram length/type/command, bad NDR payload, returned-domain mismatch, DC name with one or two leading backslashes, optional samlogon response ownership, timeout behavior in `nbt_getdc()`, and successful end-to-end interaction with a local nmbd packet socket.
