# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwe.c

LZWEncode stream filter implementation.

Key behavior:
- Defines fixed PostScript LZW special codes: reset `256`, EOD `257`, first assignable `258`.
- Uses an open-addressed hash table to map `(prefix code, byte)` sequences to dictionary codes.
- `lzw_put_code` writes variable-width codes into the output bit buffer.
- `lzw_reset_encode` resets dictionary state and preloads all single-byte codes.
- `s_LZWE_init` allocates the encoding table, emits initial reset on first process call, and initializes bit state.
- `s_LZWE_process` recognizes longest existing sequences, emits codes, adds dictionary entries, increases code width at thresholds, resets at the dictionary limit, and emits final code/EOD/final byte on `last`.

Notable dependencies:
- Shared LZW state/release from `slzwx.h`/`slzwc.c`.

Research notes:
- This older file carries the Aladdin Ghostscript public-license notice style rather than the later common license header.
- Allocation failure is marked “WRONG” because it returns `ERRC`.
