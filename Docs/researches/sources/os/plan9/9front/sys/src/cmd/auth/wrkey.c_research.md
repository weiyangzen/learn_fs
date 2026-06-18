# File Research: sources/os/plan9/9front/sys/src/cmd/auth/wrkey.c

Minimal NVRAM key writer.

Behavior:
- Declares `Nvrsafe safe`.
- Calls `readnvram(&safe, NVwrite)`.
- Fails with `sysfatal` on error, exits successfully otherwise.

Purpose:
- Uses the authsrv NVRAM path to write/update safe key material.
