# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn.c

Implements `wcscspn(s, set)`, returning the length of the initial segment of `s` containing no characters from `set`. It fast-paths empty and single-character sets, and for larger sets uses the Bloom filter helper from `wcscspn_bloom.h` before confirming exact matches.

The Bloom filter avoids false negatives but may require exact set scans for false positives.
