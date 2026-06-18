# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/parse.h

Defines parsed command and address structures for the `sam` command language.

Key contents:
- `Addr` represents text addresses: character, line, regexp, dot, dollar, plus/minus, comma, semicolon, and file-qualified address forms.
- `Cmd` represents executable commands, optional address, regexp, text, target address, nested command, count, flags, and chained block member.
- `Cmdtab` describes command parser/executor metadata: textual argument, regexp argument, address argument, defaults, count handling, terminator tokens, and function pointer.
- Default address enum values are `aNo`, `aDot`, and `aAll`.
- Declares command handlers implemented in `xec.c` plus parser/executor interfaces such as `getregexp`, `newaddr`, `address`, and `cmdexec`.

Behavior notes:
- Field aliases (`are`, `left`, `ccmd`, `ctext`, `caddr`) overlay unions used by parser and executor code.
