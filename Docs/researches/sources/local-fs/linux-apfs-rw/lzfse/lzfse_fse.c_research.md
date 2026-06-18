# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.c

## Purpose
Builds finite-state entropy decoder tables used by the LZFSE decoder.

## Main Responsibilities
- Initializes symbol decoder tables from normalized frequency histograms.
- Initializes value decoder tables for L/M/D streams, combining FSE state transition data with extra-bit counts and base values.
- Validates that cumulative frequencies do not exceed the declared number of states for plain decoder table initialization.

## Key Functions
- `fse_init_decoder_table()`: fills compact 32-bit decoder entries containing symbol, bit count, and delta.
- `fse_init_value_decoder_table()`: fills value decoder entries containing total bits, extra value bits, state delta, and base value.

## Dependencies
Includes `lzfse_internal.h`, which supplies table entry types and L/M/D configuration.

## Notes
This file is decode-only support from Apple’s BSD-licensed LZFSE code; encode-side table generation is not present in this source tree.
