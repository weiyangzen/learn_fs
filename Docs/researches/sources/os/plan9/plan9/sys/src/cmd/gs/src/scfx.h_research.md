# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfx.h

State definitions for Ghostscript CCITTFax encode/decode filters.

It defines common CCITT fax state fields:

- Client parameters such as `Uncompressed`, `K`, `EndOfLine`, `EncodedByteAlign`, `Columns`, `Rows`, `EndOfBlock`, `BlackIs1`, `DamagedRowsBeforeError`, `FirstBitLowOrder`, and `DecodedByteAlign`.
- Derived state such as `raster`, current line buffer `lbuf`, previous line buffer `lprev`, and mixed-mode `k_left`.

It defines encoder state `stream_CFE_state` with max output sizing, encoded-line buffer, and read/write counters.

It defines decoder state `stream_CFD_state` with bit/row positions, EOL counts, current polarity, 2-D run-color state, damaged-row tracking, and uncompressed-mode placeholders.

The header declares GC descriptor macros and templates `s_CFE_template` and `s_CFD_template`.

This is compression filter state, not filesystem code.
