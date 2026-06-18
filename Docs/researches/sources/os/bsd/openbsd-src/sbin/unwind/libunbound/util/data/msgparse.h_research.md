# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.h

## Role

`msgparse.h` defines the temporary DNS packet parsing structures, EDNS data structures, TTL policy globals/macros, compression-pointer helpers, and parser APIs used by `msgparse.c`, `msgreply.c`, and `msgencode.c`.

## Core Structures

`struct msg_parse` stores DNS header fields, section counts, query metadata, a fixed-size parse hashtable, and an ordered list of parsed RRsets.

`struct rrset_parse` represents one parsed RRset during packet parsing. It records hash, section, compressed owner-name pointer, decompressed owner length, type/class, flags, ordinary RR list, RRSIG list, and cumulative uncompressed RDATA size.

`struct rr_parse` represents one RR inside an RRset. Its `ttl_data` points at the TTL field in the packet, unless `outside_packet` marks generated data, and `size` records uncompressed RDATA storage size including the rdlength field.

`struct edns_data` stores OPT metadata: extended RCODE, EDNS version, Z/DO bits, UDP size, incoming options, outgoing options, outgoing in-place callback options, padding block size, and cookie state bits. `struct edns_option` is the linked-list representation for individual EDNS options.

## Constants and Macros

The header defines `PARSE_TABLE_SIZE`, `NORR_TTL`, compression-pointer macros `LABEL_IS_PTR`, `PTR_OFFSET`, `PTR_CREATE`, `PTR_MAX_OFFSET`, and `EDNS_RCODE_BADVERS`.

Global TTL policy variables include max/min TTLs, negative TTL bounds, serve-expired settings, serve-original-TTL behavior, and expired-reply TTL. Macros `PREFETCH_TTL_CALC`, `EXPIRED_REPLY_TTL_CALC`, `UPDATE_TTL_FROM_RRSET`, and `TTL_IS_EXPIRED` centralize TTL arithmetic and expiration tests.

## Public API

The header declares packet parsing (`parse_packet()`), EDNS extraction from parsed responses and query packets, RR skipping, RRset hashing and lookup, parse hashtable removal, EDNS option logging, and parsed-RR removal.

## Research Notes

The header documents the parser’s RRSIG reassociation model in detail. The structures intentionally point back into packet memory, so they are scratch objects rather than durable cache objects. Hash calculations must remain identical to `packed_rrset.c` for parser-to-cache consistency.
