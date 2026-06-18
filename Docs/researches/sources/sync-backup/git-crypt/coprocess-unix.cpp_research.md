# sources/sync-backup/git-crypt/coprocess-unix.cpp

Purpose: Unix implementation of the `Coprocess` abstraction for spawning child processes with optional stdin/stdout pipes backed by C++ streams.

Important APIs/types/functions: local `execvp` vector adapter, `Coprocess` constructor/destructor, `stdin_pipe`, `close_stdin`, `stdout_pipe`, `close_stdout`, `spawn`, `wait`, static `write_stdin`, and static `read_stdout`.

Control flow: pipe accessors lazily create POSIX pipes and wrap the parent ends in `ofhstream`/`ifhstream`. `spawn` forks; the child closes unused pipe ends, dup2s requested pipe ends onto fd 0/1, execs the command, and exits on failure. The parent closes child-side pipe ends. `wait` waits for the recorded pid and returns raw wait status.

State/persistence behavior: maintains pid, pipe file descriptors, and stream wrapper pointers. The destructor closes streams and pipe ends but does not wait for the child automatically.

Dependencies/integration: depends on POSIX `pipe`, `fork`, `dup2`, `execvp`, `waitpid`, `read`, `write`, and `close`, plus `System_error` and `fhstream`. Used by `util.cpp` command execution helpers.

Risks/test signals: callers must avoid deadlocks when writing and reading large bidirectional streams because this abstraction does not multiplex. Child lifetime is caller-managed through `wait`. Tests should cover command success/failure, stdout capture, stdin input, EINTR retry, descriptor closure, and wait status conversion by `exit_status`.
