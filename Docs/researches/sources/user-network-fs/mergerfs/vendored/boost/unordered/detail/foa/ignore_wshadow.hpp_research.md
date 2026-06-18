# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/ignore_wshadow.hpp

Purpose: Suppresses GCC `-Wshadow` warnings around FOA templates that derive from user-provided types.

Important APIs, types, and functions: No C++ APIs; it conditionally emits GCC diagnostic pragmas. Without `BOOST_UNORDERED_DETAIL_RESTORE_WSHADOW`, it pushes diagnostics and ignores `-Wshadow`; with that macro, it pops diagnostics.

Control flow: Only active under `BOOST_GCC`. The paired `restore_wshadow.hpp` header defines the restore macro and includes this file to pop the diagnostic state.

State and persistence behavior: Affects compiler diagnostic state for the current translation unit include region.

Dependencies and integration points: Included around `table_core`/`concurrent_table` definitions where empty-base inheritance from user hash/predicate/allocator types can trigger unavoidable shadow warnings.

Risks: Must be properly paired with restore to avoid suppressing warnings beyond the intended region. It is compiler-specific.

Test signals: Build tests with GCC and `-Wshadow` should compile FOA headers without warning leakage after restore.
