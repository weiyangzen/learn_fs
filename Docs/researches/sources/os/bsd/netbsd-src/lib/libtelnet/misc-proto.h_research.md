# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/misc-proto.h

## Purpose
Declares shared libtelnet glue APIs and application callbacks.

## Main Interfaces
Declares libtelnet helpers `auth_encrypt_init`, `auth_encrypt_user`, `auth_encrypt_connect`, and `printd`.

Declares application-provided callbacks: `telnet_net_write`, `net_encrypt`, `telnet_spin`, `telnet_getenv`, and `telnet_gets`.

## Dependencies
Feature users include authentication, encryption, Kerberos, SRA, and miscellaneous code.

## Risks And Notes
The library relies on the embedding telnet client/server to provide network write, event spin, environment, and input functions. This header is the boundary between libtelnet and the application.
