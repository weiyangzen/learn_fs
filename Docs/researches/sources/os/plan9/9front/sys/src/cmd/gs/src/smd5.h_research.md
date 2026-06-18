# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/smd5.h

Defines state and declarations for `MD5Encode`.

Key points:
- `stream_MD5E_state` embeds standard stream state plus `md5_state_t`.
- Documents that the filter accepts arbitrary input and emits a 16-byte digest when closed.
- Declares `s_MD5E_template` and `s_MD5E_make_stream`.

Research relevance:
- Interface for using MD5 as a Ghostscript stream filter.
