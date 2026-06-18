# sources/sync-backup/bup/dev/shquote

## Purpose
Quotes a string for safe single-quoted shell use.

## Important APIs, Types, and Functions
Accepts zero args to read stdin or one arg directly; uses sed to replace single quotes and wrap with quotes.

## Control Flow
Validates arity, obtains source text, prints a single-quoted representation with embedded quotes escaped as `'\''`.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
General dev helper for shell command construction.

## Risks and Test Signals
Risks include multiline stdin semantics and shell portability. Signal is output that a POSIX shell reinterprets as the original string.
