# File Research: sources/os/linux/linux/fs/lockd/Makefile

Purpose: Builds the Linux lockd module and documents regeneration of generated NLMv4 XDR files.

Key behavior:
- Adds `-I$(src)` for trace event headers.
- Builds `lockd.o` when `CONFIG_LOCKD` is enabled.
- Core objects include client lock/proc/xdr, host, service, server lock/share/subs, monitor, trace, generic xdr, and netlink.
- Adds NLMv4 client/server/generated XDR objects under `CONFIG_LOCKD_V4`.
- Adds procfs support under `CONFIG_PROC_FS`.
- Provides `make xdrgen` targets to regenerate `nlm4xdr_gen.{h,c}` and shared definitions from `Documentation/sunrpc/xdr/nlm4.x`.

Risk notes:
- Generated files are checked in, so normal builds do not require Python xdrgen tooling.
- Changing XDR specs without regenerating committed generated files would desynchronize server decode/encode declarations.
