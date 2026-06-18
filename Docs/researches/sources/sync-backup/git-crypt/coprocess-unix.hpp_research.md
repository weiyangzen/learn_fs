# sources/sync-backup/git-crypt/coprocess-unix.hpp

Purpose: Unix declaration of the `Coprocess` class used to run external commands with streamable stdin/stdout.

Important APIs/types/functions: class fields for `pid_t pid`, stdin/stdout pipe descriptors, `ofhstream` and `ifhstream` pointers, static read/write callbacks, deleted copy/assignment, and public methods `stdin_pipe`, `close_stdin`, `stdout_pipe`, `close_stdout`, `spawn`, and `wait`.

Control flow: no implementation flow in the header; it defines lazy pipe creation before `spawn`, stream closure, process spawn, and wait responsibilities.

State/persistence behavior: state is process and descriptor ownership. It has no persistent storage but manages OS handles that affect subprocess communication.

Dependencies/integration: includes `fhstream.hpp`, `<unistd.h>`, and `<vector>`. Selected by `coprocess.hpp` on non-Windows builds.

Risks/test signals: copy prevention avoids double-close, but raw pointers/descriptors require disciplined implementation. Tests should verify destructor cleanup and no descriptor leaks across repeated subprocess calls.
