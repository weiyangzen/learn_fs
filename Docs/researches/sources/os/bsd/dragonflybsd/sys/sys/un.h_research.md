# File Research: sources/os/bsd/dragonflybsd/sys/sys/un.h

## Summary
UNIX-domain socket address and kernel protocol declarations.

## Main Responsibilities
- Defines `sa_family_t` if needed.
- Defines `struct sockaddr_un` with 104-byte path storage.
- Defines BSD-visible `LOCAL_PEERCRED`.
- Declares kernel UNIX-domain socket request/control and rights-passing helpers.
- Defines userland `SUN_LEN()` under BSD visibility.

## Important Behavior
`sockaddr_un.sun_len` includes the terminating null in the initialized length convention. Kernel declarations cover control-message disposal/externalization and peer socket connection.

## Risks
Path storage is fixed-size and historically constrained. `SUN_LEN()` depends on a null-terminated `sun_path`.
