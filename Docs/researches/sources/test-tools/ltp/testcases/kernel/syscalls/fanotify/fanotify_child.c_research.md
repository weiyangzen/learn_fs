# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify_child.c

Purpose: tiny helper executable for fanotify tests that need a real file to execute. In this subset it is used by `fanotify24.c` when testing `FAN_OPEN_EXEC_PERM` and pre-content behavior around executable opens.

Important APIs/types/functions: only `main(void)` is defined and returns zero. There are no headers, globals, or external dependencies beyond the C runtime entry point.

Control flow: program startup enters `main()` and immediately returns success.

State/persistence behavior: no state is read or written by the helper itself. Its relevance is as a copied executable artifact on the mounted test filesystem.

Dependencies/integration: listed as a resource file by fanotify tests and copied to a mount path before execution.

Risks/test signals: failures would be indirect: inability to copy or execute this helper breaks the parent fanotify test, not this file's own logic.
