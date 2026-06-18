# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/enc-proto.h

## Purpose
Declares libtelnet encryption negotiation APIs and DES mode backend hooks.

## Main Interfaces
When `ENCRYPTION` is enabled, declares encryption lookup, init, command handlers, support/is/reply/start/end/keyid negotiation functions, auto mode toggles, status/printsub helpers, and imported application hooks.

Also declares DES CFB64 and OFB64 backend functions for encryption, decryption, initialization, negotiation, session-key setup, key-id handling, and suboption printing.

## Dependencies
Depends on `Encryptions` and `Session_Key` from `encrypt.h` and compile-time `ENCRYPTION`.

## Risks And Notes
This is a macro-gated declaration surface. DES-specific prototypes are always present under `ENCRYPTION` in this header, while actual definitions require DES/authentication compile flags.
