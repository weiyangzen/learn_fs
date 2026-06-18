# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.c

`parseutil.c` implements shared parsing and encoding utilities used by text-to-wire and wire-to-text paths. It includes generic lookup-table search by name or ID, UTC time conversion helpers, period/duration parsing, hex digit parsing, escaped-character parsing, and base32/base64 codecs.

The time code provides `sldns_mktime_from_utc()` as a portable `timegm()` equivalent. For 32-bit `time_t` builds it includes 64-bit-safe calendar conversion so DNSSEC serial-arithmetic timestamps can still be interpreted relative to a supplied `now`.

`str2period` parses DNS TTL-style duration strings with `s`, `m`, `h`, `d`, and `w` suffixes, accumulating into a 32-bit value with explicit overflow reporting. Escape parsing accepts either a three-decimal-octet escape or a single escaped literal.

The base32 code supports normal and extended-hex alphabets, padded output, and padded input validation. The base64 code supports standard base64 and unpadded base64url, skips non-base64 characters in the standard decoder, and has a helper to detect characters illegal in base64url form.

These utilities keep scalar, time, escape, and binary text encodings out of the RR-specific parser code.
