# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnat.c

NAT rule pretty-printer.

Key behavior:
- Prints map, map-block, redirect, bimap, rewrite, encap, and divert rule forms.
- Handles interface lists, family, protocol, optional filter `from/to`, translated source/destination, port maps, proxy settings, round-robin, frag, age, sticky, MSS clamp, tags, purge, and debug internals.
- Uses `printnataddr()`, `printportcmp()`, `printproto()`, and `portname()`.

Research notes:
- In rewrite destination-list output, the numeric destination branch prints `in_nsrc.na_num` while handling `in_ndst`, which looks like a copy/paste mistake.
