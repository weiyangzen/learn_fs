# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/auth-proto.h

## Purpose
Declares libtelnet authentication dispatcher and method-specific function prototypes.

## Main Interfaces
When `AUTHENTICATION` is enabled, declares authenticator lookup, initialization, command/status toggles, negotiation send/receive handlers, completion/wait helpers, debug/printsub helpers, and optional Kerberos V5 and SRA method entry points.

## Dependencies
Depends on `Authenticator` being defined by `auth.h` before inclusion and on telnet authentication compile-time feature macros such as `KRB5` and `SRA`.

## Risks And Notes
This header is feature-macro driven. Consumers only see method declarations for authentication backends compiled into the library.
