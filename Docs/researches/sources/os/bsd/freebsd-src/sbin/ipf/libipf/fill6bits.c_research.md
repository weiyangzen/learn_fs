# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/fill6bits.c

This helper fills a four-word IPv6 mask for a given prefix length.

`fill6bits()` handles `/0` and `/128` directly, otherwise initializes all words to all ones and clears/truncates words after the requested prefix. Partial words are shifted and converted with `htonl()`.

The function assumes `bits` is already in a valid range.
