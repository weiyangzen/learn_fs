# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfarc4.c

Implements Arcfour/RC4 encode and decode filter wrappers.

Key behavior:
- Defines `ArcfourDecode` and `ArcfourEncode`.
- Reads the `Key` string from the parameter dictionary.
- Initializes `stream_arcfour_state` with `s_arcfour_set_key`.
- Uses the same stream template for decode and encode because RC4 is symmetric.
- Creates read filters with `filter_read` and write filters with `filter_write`.

Dependencies:
- Uses Ghostscript filter/stream infrastructure, dictionary helpers, and `sarc4.h`.

Research notes:
- Like AES, wrapper state has no retained external pointers, so stream allocation can own the copied filter state.
