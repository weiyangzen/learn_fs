# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_test.cpp

Purpose: Comprehensive test suite for `unique_ref`, CryFS's non-null unique ownership wrapper. It verifies creation, conversion to base classes and standard smart pointers, nullcheck conversion from `unique_ptr`, dereference/get/arrow, move construction/assignment, validity after moves, swap, containers, comparisons, hashing, ordering, and type aliases.

Important APIs and types: Uses `unique_ref`, `make_unique_ref`, `nullcheck`, conversions to `unique_ptr`/`shared_ptr`, `is_valid`, `swap`, comparison/hash operators, STL containers, and local base/child/value classes.

Control flow: Tests construct objects with zero/one/two constructor parameters, transfer ownership through moves and conversions, intentionally inspect moved-from invalid state, place refs in sequence/ordered/unordered containers, and compare pointer identity/order/hash behavior.

State and persistence behavior: In-memory object ownership only. The wrapper can become invalid after move, which is explicitly tested.

Dependencies and integration points: Many CryFS components use `unique_ref` for non-null ownership while interoperating with standard smart pointers.

Risks: Moved-from invalid access, base-class conversions, and hash/order behavior are subtle. Container support can accidentally require copyability.

Test signals: Correct payload access, ownership transfer without leaks, invalid moved-from state, standard pointer conversion, container compatibility, and comparison/hash results.
