# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.c

## Role

`msgparse.c` parses DNS wire-format packets into temporary `msg_parse`, `rrset_parse`, and `rr_parse` structures. It validates packet bounds, groups RRs into RRsets, associates RRSIGs with their covered RRsets, extracts EDNS OPT metadata, and provides helpers for skipping or removing parsed RRs.

## Message and RRset Parsing

`parse_packet()` reads the DNS header, enforces at most one question, parses the query section, then parses answer, authority, and additional sections. It tolerates a missing additional OPT in one lenient case and ignores trailing spurious packet bytes.

`parse_section()` walks RRs in a section. For each RR it parses the owner name, type, class, and TTL/RDATA framing, then calls `find_rrset()` and `add_rr_to_rrset()`. The parser hashes by owner name/type/class/flags into a 32-bucket parse table, while also optimizing for sequential RRs with the same owner.

`calc_size()` computes decompressed in-memory RDATA size, expanding domain names in RDATA for types whose `sldns_rr_descriptor` marks embedded names. `skip_ttl_rdata()`, `skip_pkt_rr()`, and `skip_pkt_rrs()` safely advance over uninterested records.

## RRSIG and Section Handling

The file has detailed RRSIG grouping logic. `pkt_rrsig_covered()` reads the covered type from RRSIG RDATA. `rrset_has_sigover()`, `moveover_rrsigs()`, and `change_rrsig_rrset()` allow signatures that appear before or after their data RRset to be attached to the final dataset.

`find_rrset()` also handles NSEC-apex and negative-SOA flag differences, compares compressed names with `smart_compare()`, and handles special qtype `RRSIG` or `ANY` cases so signatures are not incorrectly split or duplicated.

If the same RRset appears in multiple sections, `add_rr_to_rrset()` drops later less-trustworthy parts rather than merging section trust levels, following the RFC 2181 RRset placement rule.

## EDNS Parsing

`parse_extract_edns_from_response_msg()` scans parsed additional RRsets for OPT, removes the selected OPT RRset from the parsed message, initializes `edns_data`, and copies incoming EDNS options into a region list.

`parse_edns_from_query_pkt()` is a direct query-path EDNS parser. It validates query-section assumptions, rejects answer/authority complications unless skipped successfully, enforces at most one additional OPT, reads EDNS version/bits/UDP size, and delegates option handling to `parse_edns_options_from_query()`.

`parse_edns_options_from_query()` handles NSID, TCP keepalive, padding, and COOKIE options. Cookie parsing validates client/server cookie lengths, remote address binding, active or configured cookie secrets, renewal/expired/future status, and creates outgoing COOKIE options where needed. It also records all parsed incoming options in `opt_list_in`.

## Research Notes

The parser stores pointers into the packet buffer until later copy/decompression. Any caller must keep the buffer alive through `parse_create_msg()` or equivalent conversion. Security-sensitive behavior centers on bounds checks, RRSIG grouping, EDNS option length handling, and DNS COOKIE validation state.
