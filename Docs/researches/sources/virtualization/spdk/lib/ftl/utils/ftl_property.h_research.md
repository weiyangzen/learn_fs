# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_property.h

Public property system API.

Defines:
- Init/deinit.
- Dump helpers for bool, uint64, uint32.
- Callback typedefs for dump, decode, and set.
- Property registration, JSON dump, decode, set, generic setter.
- Inline helper for mutable boolean properties.

Used by FTL config initialization and RPC property handling.
