# File Research: sources/os/plan9/9front/sys/src/cmd/git/objset.c

Provides an open-addressed hash set for `Object*` keyed by SHA-1. `osinit` starts with 16 slots, `osadd` linearly probes and doubles when load exceeds 50%, `osfind` returns an object by hash, and `oshas` is a boolean wrapper.

The set stores object pointers without managing references; callers own lifetime/reference discipline. It is used by traversal, caching, pack generation, and reference graph coloring.
