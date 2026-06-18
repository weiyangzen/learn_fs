# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.h

`parseutil.h` declares shared parse utility types and functions. `sldns_lookup_table` is the common integer/name mapping structure used for RR classes, algorithms, errors, and similar tables.

The API covers lookup-table search, UTC `struct tm` conversion, RFC1982-style serial timestamp conversion, TTL/period parsing with overflow reporting, hex digit conversion, base64/base64url and base32/base32hex size calculation plus encode/decode functions, and escaped-character parsing.

The header is used by both parser and formatter modules, so it forms the common support layer for DNS presentation syntax and binary encodings.
