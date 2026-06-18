# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/wrkey.c

Tiny utility that calls `readnvram(&safe, NVwrite)` to write/update nvram authentication data through the standard prompt path.

Exits fatally if nvram write fails.
