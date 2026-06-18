# sources/storage-engines/wiredtiger/test/huge/CMakeLists.txt

Purpose: build and register the `test_huge` executable. This test stresses oversized keys and values in WiredTiger objects.

Important APIs and behavior: `create_test_executable(test_huge SOURCES huge.c)` builds the binary from `huge.c`. `define_test_variants` registers the `small|-s` variant and labels it `check`, which means normal check smoke runs execute the small bounded mode rather than the full multi-gigabyte sweep.

Control flow and state: the CMake file has no runtime state. It delegates variant expansion to the repository's test CMake helpers.

Dependencies and integration: relies on top-level WiredTiger test CMake macros and the `huge.c` source. The `small` variant maps directly to `huge.c` option `-s`.

Risks and test signals: the full executable can allocate up to 4 GiB and open WiredTiger with a 10 GiB cache, so check integration intentionally constrains CI exposure. A useful test signal is that the small variant remains under check labels while full runs are left for explicit stress execution.
