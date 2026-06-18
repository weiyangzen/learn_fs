# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/exec.h

Interpreter data definitions and opcode declarations for rc.

Defines:
- external declarations for all `X*` opcode functions;
- `word`: linked list of shell words;
- `list`: stack frame containing a word list;
- `redir`: deferred redirection operation (`ROPEN`, `RDUP`, `RCLOSE`);
- `thread`: execution frame containing code vector, pc, argv stack, redirections, locals, command input, status, tree nodes, wait pid, and return link;
- `builtin`: builtin command mapping.

Declares global interpreter state: `runq`, `codebuf`, traps, builtin table, `eflagok`, and `havefork`.

Risk/notes:
- `thread.ret` is the interpreter call stack.
- Redirection stack is inherited through `startredir`.
- `NSTATUS` is tied to Plan 9 `ERRMAX`.
