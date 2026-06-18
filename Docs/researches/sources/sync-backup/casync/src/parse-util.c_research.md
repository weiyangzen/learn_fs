# sources/sync-backup/casync/src/parse-util.c

Purpose: parses and formats byte-size quantities for CLI/config-style input and output.

Important APIs/types/functions: `parse_size` recognizes numeric values with optional binary unit suffixes from bytes through exabytes, plus `K/M/G/T/P/E` aliases; `format_bytes` converts byte counts into a compact human-readable binary unit string.

Control flow/state: `parse_size` uses `strtoull`, checks suffixes against a local table, rejects fractional values that would not divide cleanly after scaling, and returns `-ERANGE`/`-EINVAL` on overflow or malformed input. `format_bytes` chooses the largest unit where the value is cleanly divisible, otherwise reports raw bytes.

Dependencies/integration: includes `time-util.h` only transitively for utility constants and `util.h` for helpers. Used by command-line parsing and status output.

Risks/test signals: decimal-looking fractional input is accepted only when exactly representable after binary scaling; unexpected whitespace/suffix combinations can be rejected. No direct test in this subset, so coverage is likely via CLI tests.

Source research group: `subset-b-009122`.
