<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_bitstring.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_bitstring.cpp

Purpose: Unit tests for WiredTiger bitstring macros and range-setting behavior.

Important APIs/types/functions: Exercises `__bit_byte`, `__bit_mask`, `__bitstr_size`, and `__bit_nset`.

Control flow: Macro tests check fixed input/output mappings. `__bit_nset` sections initialize an eight-byte vector and verify byte contents after aligned and non-aligned bit ranges are set.

State and persistence behavior: Only local vectors; no persistence.

Dependencies and integration points: Includes `wt_internal.h`; protects shared bit manipulation primitives used by block and other WiredTiger subsystems.

Risks and test signals: Off-by-one and byte-boundary errors are the key risks. Test signal is exact byte values for first/last/middle unaligned ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_bitstring.cpp -->
