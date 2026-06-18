# File Research: sources/virtualization/guestfs-tools/builder/index-scan.l

## Scope

Flex scanner for virt-builder index syntax.

## Tokens And Behavior

- Ignores comments beginning with `#` at the start of a line and increments `seen_comments`.
- Ignores blank lines.
- Recognizes section headers of the form `[A-Za-z0-9._-]`.
- Recognizes fields `key=value` and `key[subkey]=value`, allocating `struct field`.
- Recognizes indented continuation lines and strips the leading whitespace and trailing newline.
- Special-cases PGP signed-message prologue by consuming headers through the first blank line.
- Special-cases PGP signature epilogue by consuming to EOF.
- Returns `UNKNOWN_LINE` for otherwise invalid input.

## Interfaces

- Reentrant scanner with bison bridge and location tracking.
- Provides `scanner_init` and `scanner_destroy`.

## Risks And Invariants

- Scanner intentionally processes line-by-line except for PGP wrapper hacks.
- Comments are only comments at column zero.
- PGP prologue/epilogue consumption affects compatibility validation because comments are counted separately.
