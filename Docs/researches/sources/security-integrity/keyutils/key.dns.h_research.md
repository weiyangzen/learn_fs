
# sources/security-integrity/keyutils/key.dns.h

## Purpose
`key.dns.h` is the shared header for the keyutils DNS resolver helper and its AFSDB/SRV support module.

## Important APIs, Types, And Functions
It includes resolver, networking, syslog, keyutils, and standard C headers. It defines address-family and payload constants: `MAX_VLS`, `INET_IP4_ONLY`, `INET_IP6_ONLY`, `INET_ALL`, `ONE_ADDR_ONLY`, and `N_PAYLOAD`. It declares shared globals `key`, `debug_mode`, `mask`, `key_expiry`, `payload`, and `payload_index`, plus logging/error APIs, payload helpers, `dns_resolver()`, and `afs_look_up_VL_servers()`.

## Control Flow
No runtime control flow exists in the header. It documents the cross-file calling pattern: `key.dns_resolver.c` owns main, shared state, generic A/AAAA resolution, and error handling; `dns.afsdb.c` owns AFS-specific lookup and instantiation.

## State And Persistence
The declared globals carry request state for one resolver process and ultimately determine kernel key payload and timeout.

## Dependencies And Integration Points
It ties together libresolv, keyutils, syslog, sockets, and DNS helper source files. The Makefile compiles both C files into one helper.

## Risks
Global shared state makes the helper simple but not reusable as a library or thread-safe component. Constants cap payload segments and VL servers; callers must handle overflow behavior indirectly.

## Test Signals
Any DNS helper test should validate global state transitions by inspecting debug payload output or instantiated key contents.
