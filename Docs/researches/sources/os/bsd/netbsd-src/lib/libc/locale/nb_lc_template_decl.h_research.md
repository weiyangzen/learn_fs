# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template_decl.h

Read completely: 41 lines.

This header declares template-generated category helpers: `_PREFIX(create_impl)` and `_PREFIX(update_global)`, and includes the generic setlocale declaration template.

Important interactions: used by concrete NetBSD locale category files before including `nb_lc_template.h`.

Security/reliability notes: declaration-only template support.
