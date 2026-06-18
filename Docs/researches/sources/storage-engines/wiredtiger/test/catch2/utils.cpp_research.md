# Research: sources/storage-engines/wiredtiger/test/catch2/utils.cpp

## sources/storage-engines/wiredtiger/test/catch2/utils.cpp

Purpose: Shared Catch2 utility implementation for WiredTiger C++ tests.

Important functions: `utils::throw_if_non_zero` throws `std::runtime_error` on nonzero return codes; `remove_wrapper` wraps `std::remove`; `utils::wiredtiger_cleanup` removes known WiredTiger files and the home directory; `utils::break_here` emits Catch2 `INFO` for debugger breakpoints.

Control flow: cleanup intentionally ignores removal errors and deletes a fixed list of files such as `WiredTiger`, `WiredTiger.turtle`, `WiredTiger.wt`, `WiredTigerHS.wt`, backup/cursor test files, and then the directory. `break_here` records source file, line, and function.

State and persistence: affects filesystem state under the supplied DB home by removing database files. `throw_if_non_zero` affects test control flow by raising exceptions.

Dependencies/integration: used by connection/mock wrappers and tests needing cleanup or dynamic library error handling. Risks include cleanup list drift as WiredTiger creates new files, and `remove` only removing empty directories. Test signals are exceptions or Catch2 info context.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/utils.cpp -->
