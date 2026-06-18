# File Research: sources/os/bsd/dragonflybsd/sys/sys/wait.h

## Summary
Wait status macros, wait option flags, idtype definitions, and wait-family declarations.

## Main Responsibilities
- Defines status interpretation macros such as `WIFEXITED`, `WIFSIGNALED`, `WEXITSTATUS`, and BSD `WCOREDUMP`.
- Defines wait option flags including no-hang, stopped, continued, nowait, exited, trapped, and DragonFly/Linux clone support.
- Defines `WAIT_ANY`, `WAIT_MYPGRP`, `id_t`, and Solaris-style `idtype_t`.
- Declares userland wait APIs: `wait`, `waitpid`, `waitid`, `wait3`, `wait4`, and BSD `wait6`.

## Important Behavior
`WIFCONTINUED(x)` is hard-coded to status value `19`, documented as `SIGCONT`. `idtype_t` numeric values are intentionally synchronized with Solaris values.

## Risks
Wait status encoding is ABI-visible. The Solaris-compatible idtype list includes entities without exact DragonFly counterparts, so implementation support must be checked per call.
