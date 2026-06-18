# File Research: sources/os/plan9/9front/sys/src/cmd/rc/var.c

Variable and keyword table implementation for `rc`. Provides hash function, keyword initialization/lookup, global variable lookup, local-over-global lookup, set, allocation, and free.

Keywords are represented as tokenized tree nodes with `iskw` set. Variables store word-list values and optional function code vectors plus changed flags for environment synchronization.
