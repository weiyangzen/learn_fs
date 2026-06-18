# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.h

## Purpose
Defines the finite-state entropy bitstream types, table entry formats, inline decode helpers, and table initialization declarations used by LZFSE.

## Main Responsibilities
- Selects 64-bit or 32-bit FSE streams based on architecture.
- Provides mask/extract helpers for 32-bit and 64-bit bit containers.
- Defines output and input stream accumulators and inline stream push/pull/flush helpers.
- Defines `fse_decoder_entry` and `fse_value_decoder_entry`.
- Provides inline `fse_decode()` and `fse_value_decode()` routines.
- Provides `fse_check_freq()` and declarations for decoder-table builders.

## Key Types and APIs
- `fse_state`, `fse_bit_count`, `fse_in_stream`, `fse_out_stream`
- `fse_decode()`
- `fse_value_decode()`
- `fse_init_decoder_table()`
- `fse_init_value_decoder_table()`

## Dependencies
Uses Linux `types` and `string` headers.

## Notes
The decoder reads FSE input streams backward. The checked init/flush helpers reject out-of-range pointers and malformed accumulator states.
