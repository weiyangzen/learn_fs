# File Research: sources/os/bsd/netbsd-src/sys/sys/lua.h

Defines kernel Lua device ioctl ABI and kernel Lua state helpers. It provides limits for state/module names, state info/list/create/require/load structures, ioctls for listing, creating, destroying, requiring modules, and loading scripts. Kernel code gets module registration functions, `klua_State` with Lua pointer, mutex, and user-created marker, plus lock/unlock/close/newstate helpers.

Risks include ioctl buffer validation, script path handling, module lifecycle, and serialization around Lua state access.
