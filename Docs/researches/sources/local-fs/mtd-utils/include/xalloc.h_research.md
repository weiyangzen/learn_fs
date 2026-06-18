# File Research: sources/local-fs/mtd-utils/include/xalloc.h

## Purpose
Inline allocation wrappers that terminate the program on allocation failure.

## Key Elements
Defines `xmalloc`, `xcalloc`, `xzalloc`, `xrealloc`, `xstrdup`, and, under `_GNU_SOURCE`, `xasprintf`. Functions are marked `unused` to avoid warnings.

## Dependencies
Requires `sys_errmsg_die` from `common.h`, plus stdlib/string/stdarg.

## Behavior/Risks
These helpers exit the process instead of returning allocation errors, simplifying callers but making recovery impossible.
