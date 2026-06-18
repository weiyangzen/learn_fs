# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ldterm.h

## Purpose
Defines STREAMS line-discipline terminal state, buffer sizing, flow-control thresholds, EUC/PCCS/UTF-8 codeset metadata, display-width helpers, and internal state flags for `ldterm`.

## Main Interfaces
- Buffer and flow-control constants:
  - `IBSIZE`, `OBSIZE`, `EBSIZE`
  - `TTXOLO`, `TTXOHI`, `HIWAT`, `LOWAT`, `LDCHUNK`
- Mode helpers:
  - `V_MIN`
  - `V_TIME`
  - `RAW_MODE`
  - `CANON_MODE`
- EUC/codeset constants:
  - `EUCSIZE`, `EUCIN`, `EUCOUT`
  - special display widths such as `EUC_TWIDTH`, `EUC_BSWIDTH`, `UNKNOWN_WIDTH`
  - `LDTERM_DATA_VERSION`
  - `LDTERM_CS_TYPE_EUC`, `LDTERM_CS_TYPE_PCCS`, `LDTERM_CS_TYPE_UTF8`
  - `LDTERM_CS_MAX_BYTE_LENGTH`
  - `LDTERM_CS_MAX_CODESETS`
- UTF-8 range and decoding constants for Unicode planes, CJK extension ranges, variation selectors, and bit extraction.
- Data structures:
  - `ldterm_eucpc_data_t`
  - `ldterm_cs_data_user_t`
  - `ldterm_cs_data_t`
  - `ldterm_unicode_data_cell_t`
  - `ldterm_cs_methods_t`
  - `ldtermstd_state_t`
- State flags:
  - `TS_XCLUDE`
  - `TS_TTSTOP`
  - `TS_TBLOCK`
  - `TS_QUOT`
  - `TS_ERASE`
  - `TS_SLNCH`
  - `TS_PLNCH`
  - `TS_TTCR`
  - `TS_NOCANON`
  - `TS_RESCAN`
  - `TS_MREAD`
  - `TS_FLUSHWAIT`
  - `TS_MEUC`
  - `TS_WARNED`
  - `TS_CLOSE`
  - `TS_IOCWAIT`
  - `TS_IFBLOCK`
  - `TS_OFBLOCK`
  - `TS_ISPTSTTY`

## Dependencies And Relationships
Uses terminal/STREAMS types such as `termios`, `mblk_t`, `eucioc_t`, buffer-call IDs, and timeout IDs from surrounding kernel headers included by implementation files. It is the shared state contract for the `ldterm` line discipline implementation.

## Research Notes
The comments warn that codeset type values and `LDTERM_CS_TYPE_MAX` must be updated sequentially with `LDTERM_DATA_VERSION`. `ldtermstd_state_t` contains both classic terminal modes/state and multibyte character tracking, including EUC width arrays and non-EUC scratch/callback data.
