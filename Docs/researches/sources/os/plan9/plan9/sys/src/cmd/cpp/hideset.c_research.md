# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/hideset.c

Macro hideset manager used to prevent recursive macro re-expansion.

A hideset is an interned, sorted, null-terminated array of `Nlist*` entries. The module supports membership testing, adding one macro to a hideset, unioning two hidesets, initialization of the empty hideset, and debug printing.

It interns equivalent hidesets to small integer indices stored on tokens, with a fixed temporary construction limit of 32 entries.
