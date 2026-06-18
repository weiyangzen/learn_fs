# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/util.c

Read status: complete, 137 lines.

This file provides allocation helpers, string interning, and root path trimming for replica tools. `emalloc`, `erealloc`, and `estrdup` fatal on failure.

`atom` returns a canonical pointer for equal strings using a 1024-bucket hash table and chunk allocators. Atomized strings are intentionally never freed. `unroot` strips a configured root prefix and leading slashes from a path when applicable.

Filesystem relevance: supports efficient metadata storage for many repeated path, uid, and gid strings.
