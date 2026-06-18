# File Research: sources/os/plan9/9front/sys/src/cmd/mk/arc.c

Implements `Arc` allocation/freeing/debugging and updates the recursion limit used by rule application.

Key behavior:
- `newarc()` binds a prerequisite node, rule, stem, regexp matches, and optional out-of-date program into an `Arc`.
- `freearc()` frees the duplicated stem and arc object.
- `dumpa()` recursively dumps arc/node information for graph debugging.
- `nrep()` reads `NREP` from mk variables and clamps it to at least 1.

Important dependencies: `mk.h`, `rcopy`, `getvar`, `empty`, debug output through `bout`.

Notable risks:
- `freearc()` does not free regexp match strings copied by `rcopy`, so ownership is intentionally shallow/limited.
- `NREP` changes graph expansion behavior dynamically.
