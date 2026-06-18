# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfaes.c

Implements the PostScript AES decode filter wrapper used for PDF decryption.

Key behavior:
- Defines `AESDecode`.
- Reads a `Key` string from the parameter dictionary.
- Initializes `stream_aes_state` with `s_aes_set_key`.
- Creates a read filter with `filter_read` and the AES stream template.

Dependencies:
- Uses Ghostscript filter infrastructure, stream state interfaces, dictionary lookup, and `saes.h`.

Research notes:
- The filter state is copied into stream-managed storage; the wrapper passes zero rspace because it keeps no external pointers.
