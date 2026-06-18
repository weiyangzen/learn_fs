# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwd.c

LZWDecode stream filter implementation.

Key behavior:
- Defines reset, EOD, and first assignable codes relative to `InitialCodeLength`.
- Allocates a 4097-entry decode table and initializes literal codes, reset/EOD sentinels, bit state, and code-size state.
- `s_LZWD_process` reads variable-width codes in high- or low-bit-first order, supports GIF block data, handles reset and EOD codes, grows the dictionary, expands strings back-to-front, and preserves partial string copies when output buffers fill.
- Handles the classic anomalous LZW case where the next code equals the next dictionary slot.
- Includes compatibility behavior for non-GIF streams with one extra data item before reset near full dictionary.

Notable dependencies:
- Shared LZW state from `slzwx.h`.
- Debug output through `gdebug.h`.

Research notes:
- Allocation failure is marked with historical “WRONG” comment because it returns `ERRC`.
- The decoder supports both PostScript/PDF-style LZW and GIF-style block data parameters.
