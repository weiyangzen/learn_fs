# File Research: sources/os/bsd/freebsd-src/sys/sys/_offsetof.h

Minimal `offsetof` provider.

Key elements:
- Defines `offsetof(TYPE, MEMBER)` as `__builtin_offsetof(TYPE, MEMBER)` if not already defined.

Dependencies:
- Compiler builtin support.

Research notes:
- Small standalone helper for code needing offset calculations without including broader headers.
- Copyright notes indicate recent CHERI/DEC-related provenance.
