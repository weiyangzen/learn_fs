# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bzero.S

## Summary
Implements VAX `bzero()`.

## Key Details
- Uses VAX `movc5` to fill memory with zero bytes.
- Splits large zeroing requests into chunks no larger than 65535 bytes.
- Returns after clearing the final chunk.

## Notes
Like `bcopy`, it handles VAX string-instruction length limits explicitly.
