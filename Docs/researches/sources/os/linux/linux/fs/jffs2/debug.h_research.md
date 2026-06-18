# File Research: sources/os/linux/linux/fs/jffs2/debug.h

This header controls JFFS2 debug instrumentation. It defaults `CONFIG_JFFS2_FS_DEBUG` to 0, enables paranoia checks and dumps above level 0, and adds more verbose readinode/fragtree/memalloc messages above level 1. Lightweight sanity checks are always enabled through `JFFS2_DBG_SANITY_CHECKS`.

It defines legacy `D1()` and `D2()` conditional execution macros, `jffs2_dbg(level, ...)`, standardized error/warning/notice/debug message macros with PID and function names, and subsystem-specific debug macros such as `dbg_readinode`, `dbg_fragtree`, `dbg_dentlist`, `dbg_noderef`, `dbg_inocache`, `dbg_summary`, `dbg_fsbuild`, `dbg_memalloc`, and `dbg_xattr`.

The header declares all debug implementation functions in `debug.c`, then maps public macros like `jffs2_dbg_acct_sanity_check()`, `jffs2_dbg_fragtree_paranoia_check()`, and `jffs2_dbg_dump_block_lists()` either to real functions or empty statements depending on compile-time debug configuration.

Key dependencies: Linux printk/current task APIs and JFFS2 structures included indirectly by implementation users.

Notable quirk: `jffs2_dbg_dump_buffer(buf, len, offs)` macro in dump-enabled mode dereferences `*buf` when forwarding, which is unusual and likely inherited legacy macro behavior.
