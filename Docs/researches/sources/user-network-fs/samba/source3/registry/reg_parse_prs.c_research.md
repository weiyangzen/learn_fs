# sources/user-network-fs/samba/source3/registry/reg_parse_prs.c

## Purpose
`reg_parse_prs.c` implements a small parse/marshalling buffer API used by registry performance-counter RPC-style data. It manages an expandable talloc-backed byte buffer, alignment, endian-aware integer serialization, and byte-array streaming.

## Important APIs, Types, And Functions
Public functions include `prs_init()`, `prs_mem_free()`, `prs_alloc_mem()`, `prs_get_mem_context()`, `prs_grow()`, `prs_data_p()`, `prs_data_size()`, `prs_offset()`, `prs_set_offset()`, `prs_copy_data_in()`, `prs_align()`, `prs_align_uint64()`, `prs_mem_get()`, `prs_switch_type()`, `prs_uint16()`, `prs_uint32()`, `prs_uint64()`, and `prs_uint8s()`. `prs_debug()` and `tab_depth()` support structured debug output.

## Control Flow
`prs_init()` establishes marshalling or unmarshalling mode and optionally allocates an initial buffer. Marshalling mode can grow dynamic buffers on demand; unmarshalling refuses to grow and treats overrun as failure. Primitive serializers call `prs_mem_get()`, read or write values according to mode and endian flag, debug-print, and advance `data_offset`. Alignment functions pad with zero bytes in marshalling mode.

## State And Persistence
`prs_struct` owns transient buffer state: mode, endian flag, alignment, ownership, current offset, buffer size, requested growth size, data pointer, and talloc context. It does not persist data beyond the caller-managed buffer.

## Dependencies And Integration Points
It depends on Samba includes, `reg_parse_prs.h`, and `rpc_dce.h` endian/alignment constants. `reg_perfcount.h` references this API for performance counter retrieval.

## Risks And Test Signals
Tests should cover marshalling growth from zero, fixed-buffer unmarshalling overrun, offset setting, 4- and 8-byte alignment, little and big endian integer paths, uint64 low/high order, byte arrays in char and hex debug modes, and cleanup of dynamic buffers. Overflow risks around `data_offset + extra_space` and buffer-size doubling deserve boundary tests.
