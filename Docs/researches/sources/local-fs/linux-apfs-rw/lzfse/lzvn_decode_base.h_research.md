# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.h

## Purpose
Declares the low-level LZVN decoder state and decode function.

## Main Types and API
- `lzvn_decoder_state`: holds source/destination bounds, current pointers, partial literal/match state, previous distance, and end-of-stream flag.
- `lzvn_decode(lzvn_decoder_state *state)`: decodes source into destination and updates the state in place.

## Dependencies
Includes `lzfse_internal.h` for shared LZFSE/LZVN offset types and utilities.

## Notes
The header labels this as the low-level v2 API and notes that higher-level low-level APIs should switch to it.
