# File Research: sources/os/linux/linux-stable/fs/jffs2/debug.h

## Role

Defines JFFS2 debug configuration, message macros, subsystem-specific debug gates, and wrappers around sanity/paranoia/dump functions.

## Debug Configuration

- Defaults `CONFIG_JFFS2_FS_DEBUG` to 0 if unset.
- Debug level greater than 0 enables:
  - paranoia checks;
  - dumps;
  - readinode, fragtree, dentlist, noderef, inocache, summary, and fsbuild messages.
- Debug level greater than 1 enables deeper fragtree, readinode, and memory allocation messages.
- `JFFS2_DBG_SANITY_CHECKS` is always enabled for lightweight checks.

## Message Macros

- `jffs2_dbg(level, ...)` maps to `pr_debug()` when the configured level is high enough.
- `JFFS2_ERROR`, `JFFS2_WARNING`, `JFFS2_NOTICE`, and `JFFS2_DEBUG` include task PID and function context.
- Subsystem macros such as `dbg_fragtree()`, `dbg_noderef()`, and `dbg_memalloc()` either print or compile to `no_printk()`.

## Function Declarations

Declares implementation functions for:

- accounting sanity checks;
- fragment tree and accounting paranoia checks;
- prewrite erased-area validation;
- eraseblock, block-list, node-ref, fragment-tree, buffer, and node dumps.

## Wrapper Macros

- Paranoia wrappers compile to real function calls only with `JFFS2_DBG_PARANOIA_CHECKS`.
- Dump wrappers compile to real function calls only with `JFFS2_DBG_DUMPS`.
- Sanity wrappers compile to real function calls with `JFFS2_DBG_SANITY_CHECKS`.

## Research Notes

This header lets production builds keep core accounting checks while compiling out verbose diagnostics. It is included from `nodelist.h`, making debug macros broadly available across the JFFS2 implementation.
