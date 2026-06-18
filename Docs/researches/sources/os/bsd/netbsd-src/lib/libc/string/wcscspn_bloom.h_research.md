# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscspn_bloom.h

Internal inline Bloom filter helper for wide-character set membership tests used by `wcscspn()` and `wcspbrk()`. It defines a 64-byte bitset, two hash functions, an initializer over a NUL-terminated charset, and a membership predicate.

The filter is deliberately allowed to have false positives but no false negatives.
