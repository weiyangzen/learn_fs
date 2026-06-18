# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/parse.c

Parses mkfiles into variables and rules.

Key functions:
- `parse(f, fd, varoverride)` reads logical lines and dispatches include, program include, rule, or assignment handling.
- `addrules()` installs rules and records first non-meta target as default target.
- `rhead()` parses a line head, separator, attributes, optional comparison program, head words, and tail words.
- `rbody()` reads indented recipe body lines.
- `ipush()` / `ipop()` track nested input file/line context.

Supported forms:
- `<` include file.
- `<|` include output of program.
- `:` rules with attributes like `D`, `E`, `n`, `N`, `P`, `Q`, `R`, `U`, `V`.
- `=` assignments, including `U` no-export assignment attribute.

Dependencies:
- `assline`, `stow`, `setvar`, `addrule`, `execsh`, `pipecmd`, and shell-specific `charin`.
