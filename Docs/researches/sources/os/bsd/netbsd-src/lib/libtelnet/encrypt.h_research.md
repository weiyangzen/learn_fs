# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.h

## Purpose
Defines the telnet encryption method interface and shared encryption types.

## Main Interfaces
When `ENCRYPTION` is enabled, defines direction constants, DES block/schedule aliases, `VALIDKEY`, `SAMEKEY`, `Session_Key`, and `Encryptions`, the backend method table for output/input/init/start/is/reply/session/keyid/printsub.

Includes `enc-proto.h` and declares global active callbacks `decrypt_input` and `encrypt_output`.

## Dependencies
Depends on DES type names from `<des.h>` or equivalent include order, telnet encryption constants, and compile-time `ENCRYPTION`.

## Risks And Notes
The encryption ABI is callback-table based. Session keys are raw pointer/length pairs and ownership is not encoded in the type.
