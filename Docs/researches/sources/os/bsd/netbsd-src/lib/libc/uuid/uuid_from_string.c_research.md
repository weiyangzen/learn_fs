# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_from_string.c

## Purpose
Implements `uuid_from_string()`, parsing canonical UUID text into a `uuid_t`.

## Behavior
`NULL` or empty input creates a nil UUID. Otherwise the function defaults status to `uuid_s_invalid_string_uuid`, requires a 36-character canonical dashed form, rejects old dotted UUID syntax, scans 11 hex fields with `sscanf()`, then validates known variant bit patterns. On valid parse, status becomes `uuid_s_ok`; unsupported variant encodings produce `uuid_s_bad_version`.

## Dependencies
Depends on `uuid_create_nil()`, `strlen()`, `sscanf()`, and `uuid.h`.

## Risks And Notes
The scanner checks only the first dash explicitly before relying on the format string; malformed strings of the correct length generally fail conversion count. Parsed time fields are native-order struct fields, while sequence and node bytes are parsed as byte values.
