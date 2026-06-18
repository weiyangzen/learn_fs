# sources/sync-backup/rsync/io.h

Purpose: provides protocol-version compatibility wrappers for integer and long integer wire encodings, hiding whether a caller should use legacy fixed-width encoding or protocol-30 varint encoding.

Important APIs/types/functions: `read_varint30`, `read_varlong30`, `write_varint30`, and `write_varlong30`. The header relies on external `protocol_version` and lower-level I/O functions declared elsewhere: `read_int`, `read_varint`, `read_longint`, `read_varlong`, `write_int`, `write_varint`, `write_longint`, and `write_varlong`.

Control flow: each inline helper branches on `protocol_version < 30`. Older peers use fixed `read_int`/`write_int` or sentinel-based `read_longint`/`write_longint`; protocol 30 and newer use compressed variable-length encodings, preserving the caller's `min_bytes` choice for long values.

State and persistence behavior: no local state or persistence. The only state dependency is the negotiated global protocol version, which must already be set before these helpers are used. These helpers directly affect on-the-wire compatibility and batch file reproducibility because they choose the byte layout for serialized integers.

Dependencies/integration: included by rsync code that wants version-neutral integer I/O. It integrates with `io.c`'s primitive encoders and with all protocol structures whose encoding changed at protocol 30.

Risks/test signals: the main risk is using these helpers before protocol negotiation or using raw integer helpers where a protocol-conditional helper is required. Tests should compare protocol 29 and 30+ streams, including boundary values that change encoded length and `min_bytes` values for long offsets.
