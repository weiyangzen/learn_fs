# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/seexec.c

Ghostscript eexec encryption/decryption stream filters for Type 1 font data.

Key behavior:
- `s_exE_process` implements `eexecEncode` by applying `gs_type1_encrypt` over the caller-provided bytes with the stream crypt state.
- `s_exD_set_defaults` initializes decode mode as unknown, sets default `lenIV = 4`, and clears optional PFB state.
- `s_exD_process` skips Adobe-compatible leading whitespace, detects binary vs ASCII-hex eexec input from the first bytes, optionally honors enclosing PFB record boundaries, decodes hex with `s_hex_process`, decrypts with `gs_type1_decrypt`, and discards the initial `lenIV` random bytes.
- The decode template deliberately limits output buffer size to keep eexec read-ahead under the PostScript 512-source-byte requirement.

Notable dependencies:
- Type 1 crypt helpers: `gscrypt1.h`.
- Hex/scanner helpers: `sfilter.h`, `scanchar.h`, `s_hex_process`.
- Optional coordination with `PFBDecode` state through `stream_PFBD_state`.

Research notes:
- The binary/hex auto-detection includes practical compatibility behavior for malformed PostScript, including ignoring leading whitespace and sometimes `%`.
- PFB handling tries not to read beyond encrypted record boundaries by pausing at record ends or converting prematurely decoded hex sections back to binary mode.
