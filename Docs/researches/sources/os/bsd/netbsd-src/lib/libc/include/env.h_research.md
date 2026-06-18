# File Research: sources/os/bsd/netbsd-src/lib/libc/include/env.h

Private environment-management header.

Declares:
- `__getenvslot`
- `__findenvvar`
- `environ`

Threading:
- Under `_REENTRANT`, declares environment read/write/unlock helpers.
- Otherwise supplies inline no-op lock helpers returning true.

Used by libc environment functions to centralize slot lookup and locking behavior.
