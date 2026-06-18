# sources/storage-engines/tikv/components/engine_traits_tests/src/basic_read_write.rs

Purpose: Verifies that non-CF mutation/read APIs target the default column family.

Important APIs and control flow: The test opens an engine with `ALL_CFS`, writes `foo=bar` through `put`, and reads it through `get_value_cf(CF_DEFAULT, ...)`.

State, persistence, and dependencies: Persistent test state is one key in the default CF inside a temporary engine directory.

Integration points, risks, and test signals: Validates API equivalence between non-CF and default-CF variants. A failure indicates incorrect default CF mapping or write/read routing in an implementation.
