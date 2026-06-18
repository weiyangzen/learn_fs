# sources/test-tools/fio/os/windows/posix/include/sys/ioctl.h

Purpose: empty Windows `<sys/ioctl.h>` compatibility shim.

Important APIs/types: none; the source comment says the file only needs to exist on Windows and is otherwise unused.

Control flow and state: no runtime behavior.

Dependencies and integration: prevents build failures from unconditional includes in portable source.

Risks: not a real ioctl interface. Future Windows code expecting ioctl request macros or function declarations must add them or gate the include.

Test signals: compile-only coverage.
