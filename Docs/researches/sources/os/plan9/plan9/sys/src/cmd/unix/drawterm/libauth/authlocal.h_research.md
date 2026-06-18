# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/authlocal.h

This header contains one internal auth declaration.

Key contents:
- Declares `_fauth_proxy(int fd, AuthRpc *rpc, AuthGetkey *getkey, char *params)` returning `AuthInfo*`.

Important details:
- The visible implementation in this tree is named `fauth_proxy`, so this declaration reflects an internal/compatibility naming convention.
