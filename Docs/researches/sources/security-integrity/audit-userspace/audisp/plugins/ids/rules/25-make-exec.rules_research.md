# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-make-exec.rules

Purpose: tags chmod-style operations that create executable files in writable or user-controlled directories.

Important APIs and data: b64 syscall rules cover `chmod`, `fchmod`, and `fchmodat` in `/home`, `/tmp`, `/var/tmp`, and `/dev/shm`, checking execute bits via `a1&0111` or `a2&0111`, `filetype=file`, user auid filters, and key `ids-mkexec`.

Control flow: kernel audit emits matching syscall records; `model_behavior.c` maps `ids-mkexec` to a four-point session score increase.

State and persistence: installed as persistent audit rules when included in audit rule deployment.

Dependencies and integration: architecture-specific to b64 syscalls and behavior model key names.

Risks: lacks b32 coverage and misses executable creation paths not using these syscalls. It may flag legitimate build or install activity under user directories.

Test signals: chmod/fchmodat executable bit changes in the watched directories should emit `ids-mkexec` events.
