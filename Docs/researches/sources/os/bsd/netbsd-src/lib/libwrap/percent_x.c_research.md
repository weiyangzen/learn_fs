# File Research: sources/os/bsd/netbsd-src/lib/libwrap/percent_x.c

## Summary
Expands TCP wrappers `%<char>` substitutions in strings used by banners and shell commands. Expansion values come from `request_info` evaluation helpers and are sanitized for shell use.

## Main Responsibilities
- Expand `%a`, `%A`, `%c`, `%d`, `%h`, `%H`, `%n`, `%N`, `%p`, `%s`, `%u`, and `%%`.
- Replace characters outside a fixed safe set with `_` in expansion strings.
- Copy literal input characters unchanged.
- Abort the process after warning if expansion would exceed the output buffer.

## Key Interfaces
- `percent_x(char *result, int result_len, char *string, struct request_info *request)`.

## Risks
The function edits expansion strings in place, which can affect cached request fields returned by `eval_*()` helpers. On buffer overflow it calls `sleep(5)` and `exit(0)` rather than returning an error, because it may run in contexts where `tcpd_jump()` or `clean_exit()` are unsafe.
