# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.c

Termcap compatibility implementation on top of terminfo.

Key responsibilities:
- Includes generated/static `termcap_map.c` and generated `termcap_hash.c`.
- Defines global termcap compatibility variables:
  - `UP`
  - `BC`
- Implements classic termcap APIs:
  - `tgetent`
  - `tgetflag`
  - `tgetnum`
  - `tgetstr`
  - `tgoto`
- Maps two-character termcap IDs to terminfo indexes via generated perfect hashes.
- Searches user-defined capabilities when built-in mappings do not satisfy a request.
- Under `TERMINFO_COMPILE`, implements `captoinfo`, converting termcap entries to terminfo syntax.
- Converts termcap string formatting operations into terminfo `%` expressions.
- Adds default capabilities such as `bel`, `cr`, `cud1`, `ht`, `ind`, `kbs`, `kcub1`, `kcud1`, and `nel` when missing.

Role in subsystem:
- Compatibility layer for legacy termcap programs while internally using terminfo records.
