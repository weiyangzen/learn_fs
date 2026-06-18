# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.h

## Role

`msgencode.h` declares the public message-encoding API for converting `query_info`, `reply_info`, and `edns_data` structures into DNS wire-format buffers.

## API Surface

The main reply entry points are `reply_info_answer_encode()` and `reply_info_encode()`. The first is the higher-level answer encoder that derives response flags from query flags, cache/auth state, DNSSEC state, and EDNS metadata. The second regenerates a DNS packet from stored reply data and handles whole-RRset truncation and optional minimal-response suppression.

`qinfo_query_encode()` serializes a query from `query_info`. `calc_edns_field_size()`, `calc_edns_option_size()`, `calc_ede_option_size()`, and `attach_edns_record()` expose EDNS OPT sizing and appending helpers. `error_encode()` and `extended_error_encode()` build DNS error packets with optional question and EDNS data.

## Dependencies and Contracts

The header forward-declares `sldns_buffer`, `query_info`, `reply_info`, `regional`, and `edns_data`, keeping callers decoupled from the concrete parser and reply storage internals. Callers provide a scratch `regional` allocator for compression state and must supply packet-size limits such as 512, EDNS UDP size, or TCP-sized buffers.

## Research Notes

The contract distinguishes allocation failure from truncation: public functions usually return failure for memory/server errors while successful truncation still returns a valid packet. Extended errors above classic 4-bit RCODE space require EDNS attachment to be visible on the wire.
