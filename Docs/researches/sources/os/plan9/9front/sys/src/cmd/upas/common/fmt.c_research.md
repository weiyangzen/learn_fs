# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/fmt.c

This file installs an RFC 2047-ish formatter for non-ASCII header strings.

Key behavior:
- `rfc2047fmt` returns ASCII-only strings unchanged.
- If any byte is >= `0x80`, it emits `=?utf-8?q?...?=` encoding.
- Spaces become `_`; `_`, tab, `=`, `?`, and high-bit bytes become `=HH`.
- `mailfmtinstall` registers this formatter as `%U`.

Integration and risks:
- Used by upas tools that need safe mail header display/output.
- It treats input as bytes and labels as UTF-8; callers must provide UTF-8-compatible data for strict correctness.
