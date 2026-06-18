# File Research: sources/os/plan9/9front/sys/src/cmd/rc/havefork.c

Implements fork-dependent opcodes for systems with process creation: async blocks, pipelines, backquote command substitution, pipefd forms, subshells, and external command fork/exec.

Maintains a dynamic `waitpids` list so `Waitfor()` only consumes children owned by this shell context. Child paths clear the wait list before running nested code.

Filesystem/process relevance: creates OS pipes, maps them into shell redirection stacks, returns `/fd/N` pipe names for pipefd expressions, and coordinates parent-side wait/status handling.
