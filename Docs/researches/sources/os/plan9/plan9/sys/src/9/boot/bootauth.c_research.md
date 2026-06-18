# File Research: sources/os/plan9/plan9/sys/src/9/boot/bootauth.c

Boot authentication agent startup.

Key behavior:
- If `/boot/factotum` is unavailable, falls back to `glenda()` behavior by setting `#c/hostowner` to `$user` or `glenda`.
- Otherwise forks `/boot/factotum` with options from `debugfactotum`, `factotumopts`, CPU/user mode flags, service name `factotum`, and optional auth address.
- Waits until `/mnt/factotum` exists before returning.

This establishes boot-time authentication identity and key service.
