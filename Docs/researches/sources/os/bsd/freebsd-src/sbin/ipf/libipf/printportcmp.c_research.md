# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printportcmp.c

Port comparison clause printer.

Key behavior:
- Maps comparison enum values to text operators.
- Prints in/out range, inclusive range, and simple comparison forms.
- Resolves simple port names with `portname()`.

Research notes:
- Assumes `frp_cmp` indexes the local operator table safely.
