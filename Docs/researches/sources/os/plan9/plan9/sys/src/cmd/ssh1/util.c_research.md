# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/util.c

Shared utilities for SSH1 tools.

Key responsibilities:
- Error/debug output and zeroing allocation wrappers.
- Process cleanup via registered kill list.
- Reads newline-terminated SSH identification strings.
- Computes SSH1 session id from host/server public moduli and cookie.
- Writes syslog entries.
- Builds host alias list from ndb/dns.
- Rebinds terminal factotum when needed.

Important functions:
- `error`, `debug`, `emalloc`, `erealloc`.
- `atexitkill`, `atexitkiller`.
- `readstrnl`, `calcsessid`.
- `setaliases`, `privatefactotum`.

Risks/quirks:
- `sshlog` calls `va_start`/`va_end` before using `fmtvprint`, which is suspicious in modern C terms.
- `trim` sorts and deduplicates aliases by mutating tokenized string.
