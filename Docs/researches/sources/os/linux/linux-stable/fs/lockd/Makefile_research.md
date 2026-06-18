# File Research: sources/os/linux/linux-stable/fs/lockd/Makefile

Build composition for the kernel lock manager (`lockd`).

Key points:
- Adds `-I$(src)` for trace event headers.
- Builds `lockd.o` when `CONFIG_LOCKD` is enabled.
- Core objects include client lock/proc/XDR, host cache, service code, server locking/sharing/proc/subs, NSM monitor, trace, XDR, and netlink.
- `CONFIG_LOCKD_V4` adds NLMv4 client XDR, server v4 procedures, and generated NLMv4 server XDR.
- `CONFIG_PROC_FS` adds procfs support.
- Provides an `xdrgen` developer target to regenerate checked-in generated files from `Documentation/sunrpc/xdr/nlm4.x`.
