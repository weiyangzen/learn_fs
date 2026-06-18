# File Research: sources/os/plan9/9front/sys/src/cmd/upas/unesc/unesc.c

`upas/unesc` decodes a simplified RFC 2047-like `=?charset?encoding?text?=` token stream from stdin to stdout. It skips the charset and encoding names, decodes `=XX` hex escapes inside the encoded text, and writes other bytes literally.

It does not implement full RFC 2047 semantics or charset conversion; it is a small stream utility for encoded-word unescaping.
