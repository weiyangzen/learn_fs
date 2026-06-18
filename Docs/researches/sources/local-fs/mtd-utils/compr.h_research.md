# File Research: sources/local-fs/mtd-utils/compr.h

## Purpose
Public interface for the JFFS2 compression subsystem in this user-space build.

## Key Elements
Defines enabled compressors, priorities, compression modes, kernel compatibility shims (`kmalloc`, `printk`, `KERN_*`), a minimal `list_head`, and `struct jffs2_compressor`.

## Dependencies
Includes stdio/stdlib/stdint and `linux/jffs2.h`. Declares zlib, rtime, and LZO compressor init/exit functions when configured.

## Behavior/Risks
The header intentionally emulates kernel APIs in user space. Callers must treat returned compression buffers and allocated stats/list strings as heap-owned.
