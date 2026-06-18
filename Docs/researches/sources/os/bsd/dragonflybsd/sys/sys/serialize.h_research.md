# File Research: sources/os/bsd/dragonflybsd/sys/sys/serialize.h

This header defines DragonFly's lightweight `lwkt_serialize` synchronization primitive and its kernel API.

Key responsibilities:
- Defines `struct lwkt_serialize`:
  - atomic interrupt interlock
  - last-owning thread pointer
- Defines initializer `LWKT_SERIALIZE_INITIALIZER`.
- Defines ownership assertion helpers:
  - `IS_SERIALIZED()`
  - `ASSERT_SERIALIZED()`
  - `ASSERT_NOT_SERIALIZED()`
- Defines `lwkt_serialize_t`.
- Declares kernel functions:
  - init
  - enter/adaptive enter
  - try
  - exit
  - handler disable/enable/call/try

Important invariants:
- The header explicitly warns the primitive is not recursive and is not deadlock-safe like tokens.
- It is meant to serialize across blocking conditions while being fast in the common case.
- Ownership tracking uses `last_td` and `curthread` for assertions.

Research notes:
- This is a DragonFly-specific low-level serialization primitive used where a full token would be heavier.
