# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtbegin.S

SH3 hand-written `crtbegin` implementation. It defines legacy constructor/destructor lists, EH/JCR anchors, `__dso_handle`, initialization flags, weak helper references, and PIC/non-PIC access macros.

The constructor helper registers frame info, optionally registers Java classes, and walks `.ctors` in reverse. The destructor helper finalizes shared objects, walks `.dtors`, and deregisters frame info. Both are wired into `.init` / `.fini` with a branch-oriented helper macro.
