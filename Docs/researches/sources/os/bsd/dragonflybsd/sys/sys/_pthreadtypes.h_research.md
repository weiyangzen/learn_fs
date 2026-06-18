# File Research: sources/os/bsd/dragonflybsd/sys/sys/_pthreadtypes.h

Read completely: 81 lines.

This header provides namespace-light pthread type declarations.

Key contents:
- Forward declarations for internal pthread object structs.
- Opaque pointer typedefs for thread, attributes, barriers, conditions, mutexes, rwlocks, and spinlocks.
- `pthread_key_t` as `int`.
- `pthread_once_t` as a partly public `struct __pthread_once_s` with state and ABI spare pointer.

Security/reliability notes:
- No executable logic. ABI stability matters because public pthread types are used in many libc and application interfaces.
