# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/dname.h

`dname.h` declares the DNS domain-name utility interface implemented by `dname.c`. It documents that routines operate on DNS wire-format domain names, either uncompressed in memory or compressed inside an `sldns_buffer`, and defines `MAX_COMPRESS_PTRS` as the compression-pointer loop limit.

The parsing and validation API includes `query_dname_len()` for uncompressed query names, `dname_valid()` for resident uncompressed names, and `pkt_dname_len()` for compressed packet names with pointer checking. Case and comparison APIs include `query_dname_tolower()`, `pkt_dname_tolower()`, `query_dname_compare()`, and `dname_pkt_compare()`. Hashing and copying APIs include `dname_query_hash()`, `dname_pkt_hash()`, `dname_pkt_copy()`, and `dname_buffer_write()`.

The header also exposes label and hierarchy utilities: label counting with optional size reporting, label-wise comparison with matching-suffix count, prefix and label-presence checks, strict and inclusive subdomain tests, root detection, removal of one or more leading labels, and conversion to debug printable forms through `dname_print()` and `dname_str()`. DNSSEC and zone-order helpers include RRSIG label counting, wildcard-name detection, canonical RFC 4034-style label comparison, whole-name canonical comparison, and shared-topdomain lookup.

Callers are expected to pass valid uncompressed names to most non-packet routines and provide the packet buffer when compression pointers may need to be resolved. The API is shared by message parsing/encoding, packed RRset handling, local-zone and auth-zone ordering, DNSSEC validation, and resolver cache/key comparisons.
