# File Research: sources/os/bsd/dragonflybsd/sys/sys/timers.h

Basic timers compatibility header.

Key contents:
- Includes `sys/time.h`.

Role:
- Provides the historical `<sys/timers.h>` include path for code expecting it.
- Contains no additional types or functions beyond what `sys/time.h` provides.

Research notes:
- This is a compatibility shim.
