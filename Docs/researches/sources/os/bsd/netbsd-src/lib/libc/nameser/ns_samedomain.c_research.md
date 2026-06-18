# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_samedomain.c

Read completely: 216 lines.

This file implements textual DNS-domain relationship helpers, compiled differently for `_LIBRESOLV` and `_LIBC`. Under `_LIBRESOLV`, it provides `ns_samedomain` and `ns_subdomain`; under `_LIBC`, it provides `ns_makecanon` and `ns_samename`.

`ns_samedomain` trims unescaped trailing dots, treats an empty candidate ancestor as root, compares only whole-label suffixes, and avoids matching escaped separator dots. `ns_makecanon` copies a name with exactly one canonical trailing dot while preserving escaped dots. `ns_samename` canonicalizes both names and compares case-insensitively.

Security/reliability notes: `ns_makecanon` checks output size and returns `EMSGSIZE` on overflow. These functions operate on presentation strings, not wire-format names; escaped-dot handling is the main correctness edge.
