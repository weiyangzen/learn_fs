# File Research: sources/os/plan9/9front/sys/src/cmd/aux/searchfs.c

`searchfs` is a custom 9P filesystem over an in-memory ASCII database. It exposes `search` and `stats` files under a mounted root. Clients write URL-style queries to `search`, then read matching database lines back.

Search strings are parsed as `tag=val&...`; supported tags are `search` and `skip`. Multiple `search` terms are split on whitespace and matched case-insensitively. The longest term becomes a Boyer-Moore-like quick matcher; remaining terms are exact line filters.

The filesystem implements its own 9P message loop and fid table instead of lib9p. It supports version, attach, walk, open, read, write, clunk, and stat; create/remove/wstat/auth are rejected. Flush requests are ignored by design.

Limitations: explicitly ASCII-oriented; database is read fully into memory; `stats` currently reads as empty; root directory read only returns the `search` entry even though `stats` is walkable/stat-able.
