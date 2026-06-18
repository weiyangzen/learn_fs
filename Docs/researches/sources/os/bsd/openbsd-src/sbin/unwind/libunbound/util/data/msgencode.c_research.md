# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.c

## Role

`msgencode.c` encodes Unbound DNS query and reply data structures back into DNS wire-format packets. It handles DNS name compression, RRset section insertion, TTL adjustment, truncation behavior, EDNS OPT attachment, EDE size trimming, minimal responses, local-alias insertion, and error response construction.

Although this file is under the OpenBSD `unwind` vendored `libunbound` tree in subset A, its domain is DNS resolver message serialization rather than filesystem logic.

## Main Implementation

The file builds an in-message compression tree with `compress_tree_node`. `compress_tree_search()`, `compress_tree_lookup()`, `compress_tree_store()`, `write_compressed_dname()`, `compress_owner()`, `compress_any_dname()`, and `compress_rdata()` maintain compression targets and emit compressed owner names or RDATA names. Compression is capped by `MAX_COMPRESSION_PER_MESSAGE` to bound CPU cost and avoids pointer chains for compatibility.

`packed_rrset_encode()` writes a `ub_packed_rrset_key` plus `packed_rrset_data` as one or more DNS RRs, optionally including data RRs and/or RRSIGs. It filters DNSSEC records when DNSSEC is not requested, applies fixed/upstream-zero/absolute/expired TTL rules, round-robins data RRs, and recompresses compressible RDATA types by consulting `sldns_rr_descriptor`.

`insert_section()` serializes answer, authority, and additional sections. It trims a failing RRset back to its section start when packet space runs out. Additional-section handling emits ordinary RRs first and RRSIGs afterward when DNSSEC is enabled.

`reply_info_encode()` writes the DNS header and question, then serializes local aliases, answer, authority, and additional sections. It handles whole-RRset truncation, TC-bit setting for answer/authority truncation, and minimal-response suppression for clear positive or negative answers.

## EDNS and Error Encoding

`calc_edns_field_size()`, `calc_edns_option_size()`, and `calc_ede_option_size()` estimate OPT-record space from outgoing EDNS option lists. `ede_trim_text()` removes EDE extra text, and can unlink `LDNS_EDE_OTHER` options when the text would no longer be useful.

`attach_edns_record_max_msg_sz()` appends an OPT RR, writes outgoing callback/module EDNS options, reserves padding when requested, and respects an explicit maximum packet size. `reply_info_answer_encode()` chooses reply flags, reserves EDNS space before encoding the base response, and retries EDNS attachment with full EDEs, trimmed EDE text, or EDE removal.

`qinfo_query_encode()` emits a basic outbound query packet. `extended_error_encode()` and `error_encode()` build QR/RA error replies, preserve RD/CD, include the question when available, and attach EDNS when it fits so extended RCODEs can be conveyed.

## Research Notes

Correctness depends on buffer-position discipline and count patching after section writes. Truncation is intentionally RRset-granular except additional-section omission, and EDNS/EDE handling is opportunistic so a response can still be sent when optional metadata does not fit.
