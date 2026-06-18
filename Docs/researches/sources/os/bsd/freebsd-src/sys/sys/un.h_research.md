# File Research: sources/os/bsd/freebsd-src/sys/sys/un.h

UNIX-domain socket address and local socket option ABI header.

Key responsibilities:
- Defines `sa_family_t` if needed.
- Defines `SUNPATHLEN` as 104 bytes, preserving historical mbuf-era binary compatibility.
- Defines `struct sockaddr_un` with length, family, and pathname fields.
- Under BSD visibility, defines `SOL_LOCAL`, local socket options for peer credentials and credential passing, vendor option base, and userland `SUN_LEN()` length helper.

Dependencies:
- Includes `sys/cdefs.h` and `sys/_types.h`.

Notable risks:
- The pathname limit is intentionally retained for ABI compatibility even though the original mbuf constraint no longer applies.
- `SUN_LEN()` uses `strlen`, so callers must pass initialized, NUL-terminated pathname fields.
