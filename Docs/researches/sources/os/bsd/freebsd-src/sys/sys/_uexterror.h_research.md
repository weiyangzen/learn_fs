# File Research: sources/os/bsd/freebsd-src/sys/sys/_uexterror.h

User ABI extended error record.

Key elements:
- Defines `struct uexterror` with version, error, category, source line, flags, reserved fields, two 64-bit parameters, and a fixed 128-byte message buffer.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Fixed-size representation suitable for copying to userland.
- Complements kernel pointer-based `struct kexterr`.
