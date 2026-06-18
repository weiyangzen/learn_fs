# File Research: sources/os/plan9/9front/sys/src/cmd/mk/parse.c

Parses mkfiles into variables and rules.

Key behavior:
- `parse()` reads logical lines, supports include files (`<`) and include programs (`<|`), handles assignments, and stores rules with recipe bodies.
- `rhead()` splits rule/assignment heads, parses assignment attributes and rule attributes (`D`, `E`, `n`, `N`, `P`, `Q`, `R`, `U`, `V`).
- `rbody()` captures indented recipe lines after a rule.
- `addrules()` records the first non-meta rule as default target candidates.
- Maintains include file/line stack with `ipush`/`ipop`.

Important dependencies: `mk.h`, `assline`, `stow`, `addrule`, `pipecmd`, `waitup`, `execinit`.

Notable risks:
- Include programs execute during parsing.
- Assignment override semantics depend on `S_OVERRIDE` and `S_WESET`.
