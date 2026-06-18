# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/seexec.c

Implements Type 1 `eexecEncode` and `eexecDecode` stream filters.

Key points:
- `s_exE_process` encrypts input bytes with `gs_type1_encrypt`, preserving Ghostscript stream cursor conventions.
- `s_exD_set_defaults` initializes binary/hex detection, `lenIV`, PFB record limits, and optional underlying PFB state pointer.
- `s_exD_process` skips leading whitespace, detects whether initial encrypted data is binary or ASCII hex, handles PFB binary record limits, decodes hex where needed, decrypts with `gs_type1_decrypt`, and skips the initial random `lenIV` bytes.
- Decode attempts to avoid reading past encrypted data by respecting PFB record boundaries and by limiting eexec output buffer sizing.
- Hex decoding tolerates leading whitespace and, for compatibility, can ignore stray `%` at error boundaries.

Dependencies and interactions:
- Uses `sfilter.h` state declarations, `gscrypt1.h` Type 1 cipher helpers, and `s_hex_process` from `sstring.c`.
- Can cooperate with a lower `PFBDecode` stream through `stream_exD_state.pfb_state`.

Research relevance:
- This is the PostScript Type 1 font encrypted-data filter implementation.
