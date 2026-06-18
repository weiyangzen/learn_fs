
## sources/storage-engines/wiredtiger/ext/page_log/palite/CMakeLists.txt

Purpose: builds `wiredtiger_palite`, a C++20 SQLite-backed implementation of WiredTiger's page log interface.

Integration: checks compiler support with minimum GNU 13, Clang 17, or MSVC 16.10, warns and returns when too old, then sets C++20 without extensions. The module links `wt::sqlite3`, includes WiredTiger headers, and applies C++ diagnostics. Linux builds add `-z,nodelete` and `--exclude-libs,ALL` to avoid sanitizer/library lifetime and symbol issues. Darwin builds run `dsymutil` after build.

State: no runtime state here, but the build controls availability of the persistent PALite SQLite backend. Risks include compiler-version variable assumptions, silently skipping the build on older compilers, and platform-specific linker behavior. Test signals include compiler-gated configure tests, Linux sanitizer builds, macOS dSYM generation, and loading the module with SQLite linked.
