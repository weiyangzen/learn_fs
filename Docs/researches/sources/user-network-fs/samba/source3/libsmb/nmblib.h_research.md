# sources/user-network-fs/samba/source3/libsmb/nmblib.h

## Purpose
This header declares the low-level NetBIOS packet and name helper API implemented by `nmblib.c`. It is the interface used by name resolution, unexpected packet handling, and older SMB client datagram code to build, parse, inspect, copy, and send NBT packets.

## Important APIs, Types, And Functions
The header includes `nameserv.h` for `struct packet_struct`, `struct nmb_name`, packet types, resource records, and datagram/NMB packet shapes. It declares packet lifecycle functions (`copy_packet`, `free_packet`, `parse_packet`, `parse_packet_talloc`), builders/senders (`build_packet`, `send_packet`, `cli_set_message`), name helpers (`put_name`, `make_nmb_name`, `nmb_name_equal`, `nmb_namestr`, `name_mangle`, `name_extract`, `name_len`), transaction/debug helpers (`packet_trn_id`, `debug_nmb_packet`), and address/list helpers (`matching_len_bits`, `sort_query_replies`, `match_mailslot_name`).

## Control Flow And Integration
Callers typically create or parse `packet_struct` instances, inspect transaction IDs, validate packet contents, and free or talloc-own the result. `namequery.c` uses these declarations for every NetBIOS name query and node status transaction. Datagram consumers use `match_mailslot_name` to filter mailslot traffic.

## State And Persistence
The header has no state. It exposes functions with two ownership styles: SMB allocator ownership for `parse_packet`/`copy_packet`, and talloc ownership for `parse_packet_talloc` and `name_mangle`.

## Dependencies
It depends on `nameserv.h` and the Samba global include environment for `TALLOC_CTX`, `bool`, `size_t`, `fstring`, `struct in_addr`, and packet type definitions.

## Risks And Test Signals
The main risks are ownership confusion between malloc-style and talloc-style packet APIs, and callers passing insufficient buffers to builders or name extraction helpers. Compile tests should include both NMB and DGRAM consumers; runtime tests should pair the declarations with `nmblib.c` parser/builder round trips.
