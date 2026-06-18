# sources/user-network-fs/samba/source3/libsmb/nmblib.c

## Purpose
This file implements low-level NetBIOS Name Service and datagram packet support. It encodes and decodes RFC1001/1002 NetBIOS names, parses and builds NMB and DGRAM packets, copies/frees packet structures, sends UDP packets, formats debug output, sorts name-query reply records, and provides small SMB message buffer helpers.

## Important APIs, Types, And Functions
Exported functions include `global_nmbd_socket_dir`, `debug_nmb_packet`, `put_name`, `nmb_namestr`, `copy_packet`, `free_packet`, `packet_trn_id`, `parse_packet`, `parse_packet_talloc`, `make_nmb_name`, `nmb_name_equal`, `build_packet`, `send_packet`, `match_mailslot_name`, `matching_len_bits`, `sort_query_replies`, `name_mangle`, `name_extract`, `name_len`, and `cli_set_message`.

Internal parser/builder helpers include `handle_name_ptrs`, `parse_nmb_name`, `put_nmb_name`, `parse_alloc_res_rec`, `put_res_rec`, `put_compressed_name_ptr`, `parse_dgram`, `parse_nmb`, `build_dgram`, `build_nmb`, `name_interpret`, and `name_ptr`.

## Control Flow
Packet parsing starts at `parse_packet`, allocates a `packet_struct`, fills common metadata, and dispatches to `parse_nmb` or `parse_dgram`. `parse_nmb` reads the 12-byte NMB header, optional question, and resource-record arrays, using `parse_nmb_name` to decode compressed NetBIOS names and `parse_alloc_res_rec` to bounds-check record data. `parse_dgram` reads the datagram header, optional source/destination names, and bounded payload data.

Packet building mirrors parsing through `build_packet`, `build_nmb`, and `build_dgram`. `build_nmb` writes flags and record counts, encodes the question name, writes answer/name-server/additional records, and uses compressed-name-pointer encoding for registration/refresh/release requests where RFC behavior requires it. `send_packet` builds into a 1024-byte stack buffer and sends over UDP through `send_udp`, which retries transient Linux `ECONNREFUSED` notifications.

Name helpers convert between plain names, NetBIOS 16-byte names, and DNS-compatible encoded forms. `name_mangle` returns the wire-format name with configured scope, while `name_extract` and `name_len` parse names from arbitrary buffers with compression-pointer support. `matching_len_bits` and `sort_query_replies` rank query response records by address closeness.

## State And Persistence
The file has almost no persistent state. `global_nmbd_socket_dir` reads configuration dynamically. `sort_query_replies` uses a static `sort_ip[4]` scratch buffer during `qsort`, making that operation non-reentrant. Packet copies allocated by the SMB allocator must be released by `free_packet`; talloc copies from `parse_packet_talloc` are owned by the supplied context.

## Dependencies And Integration Points
This file depends on `nameserv.h` packet structures through `nmblib.h`, Samba byte-order macros, charset conversion helpers, loadparm settings for NetBIOS scope and nmbd socket directory, debug infrastructure, and socket send APIs. `namequery.c` relies on its packet build/parse, transaction ID, name construction, and debug functions for all NBT network operations.

## Risks And Edge Cases
NBT name compression is a high-risk parser area; the code caps pointer recursion and scope loops but malformed packets still exercise many bounds checks. `put_res_rec` does not perform an explicit per-record buffer check around the final memcpy except through caller length preflights, so builder callers must pass accurate lengths. `match_mailslot_name` performs pointer arithmetic before the datagram data buffer and relies on SMB datagram layout assumptions. `sort_query_replies` is not thread-safe because of static comparator state. Many APIs assume IPv4-era NetBIOS packet sizes and a 1024-byte send buffer.

## Test Signals
Tests should cover valid and malformed compressed names, pointer loops, overlong scopes, NMB query/response/resource records, datagram parsing with and without names, build-then-parse round trips, registration packets with compressed additional records, wildcard name encoding, name scope handling, talloc vs malloc packet ownership, `send_packet` length failures, mailslot matching, and sort order by shared address prefix.
