# sources/user-network-fs/samba/source3/registry/reg_init_full.h

## Purpose
`reg_init_full.h` declares the full registry initialization entry point.

## Important APIs, Types, And Functions
It exposes `WERROR registry_init_full(void)`.

## Control Flow
Callers use this API when they need the registry database initialized and every configured virtual backend registered in the hook cache.

## State And Persistence
The header contains no state. The implementation initializes persistent registry data and process-local hook-cache mappings.

## Dependencies And Integration Points
It is consumed by daemon or service setup code that needs the complete registry view rather than a limited smbconf or basic view.

## Risks And Test Signals
Compile tests should ensure callers include the correct base registry types before this header. Runtime coverage belongs to `reg_init_full.c`, especially backend registration coverage.
