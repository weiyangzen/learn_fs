# File Research: sources/os/bsd/dragonflybsd/sys/sys/kenv.h

Defines constants for the `kenv(2)` syscall: get, set, unset, and dump operations, plus maximum name/value lengths of 128 bytes. This is a compact user/kernel ABI header for kernel environment variables.

No direct VFS logic, but boot/kernel environment values often feed mount/root/device configuration.
