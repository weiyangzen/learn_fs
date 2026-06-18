# File Research: sources/os/plan9/9front/sys/src/cmd/grep/sub.c

Regex allocation and construction helpers for `grep`. It uses `sbrk` chunk allocation, allocates states and regex nodes, builds concatenation/star/or fragments, patches dangling next links, combines multiple patterns, reads pattern input, and can print regex graphs for debugging.

`addcase` optimizes large alternations of byte classes into `Tcase` dispatch tables when the number of alternatives exceeds `Caselim`, improving transition computation speed.
