# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/pwd.h

Defines `struct passwd50` with 32-bit `pw_change` and `pw_expire` fields, plus inline converters between modern `struct passwd` and `passwd50`.

It declares old password database APIs returning or filling `passwd50`, and corresponding modern `__*50` APIs using `struct passwd`.

Filesystem relevance is indirect: passwd records include home directories and shells and are commonly consumed by filesystem utilities.
