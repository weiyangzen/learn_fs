# File Research: sources/os/bsd/freebsd-src/sbin/setkey/vchar.h

## Summary
Small shared value-buffer type for the `setkey` lexer/parser.

## Main Elements
- Defines `vchar_t` with `u_int len` and `caddr_t buf`.
- Used for parsed strings, keys, policy buffers, port strings, address flags, and hardware-interface names.

## Dependencies And Integration
Included by `parse.y` and `token.l`.
