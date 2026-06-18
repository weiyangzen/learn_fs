# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.h

Header for the MD5Encode stream filter.

Key contents:
- Defines `stream_MD5E_state` with common stream state plus `md5_state_t`.
- Declares GC state macro, `s_MD5E_template`, and `s_MD5E_make_stream`.

Notable dependencies:
- `md5.h`.
- Stream types from `scommon.h`/`strimpl.h` in users.

Research notes:
- The header documents filter semantics: arbitrary input, 16-byte digest on close.
