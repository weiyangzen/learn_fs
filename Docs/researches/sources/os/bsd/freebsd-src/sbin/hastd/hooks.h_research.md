# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hooks.h

Read completely: 48 lines.

This header declares the HAST hook execution API.

Key responsibilities:
- Declares hook subsystem initialization and finalization.
- Declares child-status handling for a known PID/status pair.
- Declares periodic hook health checking.
- Declares variadic and `va_list` forms of hook execution.

Important interactions:
- Consumed by the daemon parent and role/event code that needs to run configured external commands.

Reliability notes:
- The variadic hook interface requires a NULL-terminated argument list, enforced by assertions in `hooks.c`.
