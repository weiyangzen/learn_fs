# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.c

Shared font serialization output helper for the FAPI FreeType bridge.

Key points:
- Implements `WRF_init`, `WRF_wbyte`, `WRF_wtext`, `WRF_wstring`, `WRF_wfloat`, and `WRF_wint`.
- `WRF_output` writes into a caller buffer but always increments `m_count`, allowing callers to discover required size even when the buffer is too small.
- Supports optional Type 1 eexec-style byte encryption using key `55665`, factor `52845`, and offset `22719`.
- `WRF_wfloat` and `WRF_wint` format through `sprintf`.

Dependencies and interactions:
- Includes `wrfont.h` and `stdio_.h`.
- Used by `write_t1.c` and `write_t2.c` for serializing minimal font wrappers for FreeType.

Research relevance:
- Core buffered output and encryption utility for Ghostscript’s FAPI font serialization path.
