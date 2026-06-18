# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcopy.S

## Summary
Implements VAX `bcopy()`.

## Key Details
- Detects source and destination ordering to choose forward or backward copying for overlap safety.
- Uses VAX `movc3`.
- Splits large copies into chunks no larger than 65535 bytes.
- Returns without work when source and destination are equal.

## Notes
The chunking reflects `movc3` length operand limits.
