# sources/user-network-fs/samba/source3/registry/reg_init_basic.h

## Purpose
`reg_init_basic.h` declares the common and basic registry initialization entry points.

## Important APIs, Types, And Functions
It exposes `registry_init_common()` and `registry_init_basic()`, both returning `WERROR`.

## Control Flow
Consumers call `registry_init_basic()` when they need database setup without all virtual hooks, or `registry_init_common()` when they will perform additional registration before closing the database.

## State And Persistence
The header has no state. Its implementation initializes persistent registry data and the in-memory hook cache.

## Dependencies And Integration Points
It is included by `reg_init_full.c` and `reg_init_smbconf.c` to share the common initialization path.

## Risks And Test Signals
Compile tests should ensure `WERROR` is visible through includers. Behavioral coverage belongs to the implementation, especially database close semantics and error propagation.
