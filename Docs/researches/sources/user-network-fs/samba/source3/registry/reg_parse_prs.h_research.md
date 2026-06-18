# sources/user-network-fs/samba/source3/registry/reg_parse_prs.h

## Purpose
`reg_parse_prs.h` declares the parse/marshalling stream structure and helpers used by registry performance-counter code.

## Important APIs, Types, And Functions
It defines `prs_struct` with mode, endian, alignment, dynamic ownership, offset, buffer size, growth size, buffer pointer, and talloc context. It defines `MARSHALL`, `UNMARSHALL`, `MARSHALLING()`, `UNMARSHALLING()`, `RPC_PARSE_ALIGN`, and `prs_init_empty()`. It declares buffer lifecycle, growth, offset, alignment, memory, mode-switch, and primitive streaming functions.

## Control Flow
Callers initialize a `prs_struct`, stream primitive values or bytes in marshalling/unmarshalling mode, inspect output with `prs_data_p()` and offsets, then free dynamic buffer memory with `prs_mem_free()` when appropriate.

## State And Persistence
The structure is caller-owned transient state. Dynamic buffer ownership is explicit through `is_dynamic` and `mem_ctx`.

## Dependencies And Integration Points
The API is included by performance counter registry headers and code needing RPC-like binary packing.

## Risks And Test Signals
Compile tests should ensure macro mode checks work in both directions. Runtime tests should cover dynamic and non-dynamic buffers, endian fields, alignment, and lifetime rules for `prs_alloc_mem()` versus `prs_mem_free()`.
