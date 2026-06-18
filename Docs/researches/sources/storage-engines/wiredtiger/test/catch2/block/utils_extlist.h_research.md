<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.h -->
# sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.h

Purpose: Type and function declarations for extent-list test utilities.

Important APIs/types/functions: Defines `utils::off_size` with `end()`, `utils::off_size_expected`, declarations for print/allocation/search/free/verify helpers, `operator<`, and stream operators.

Control flow: Header contains lightweight constructors and declarations only.

State and persistence behavior: No direct state; declared helpers manage `WT_EXTLIST` and node lifetime in tests.

Dependencies and integration points: Included by block extent-list and block API tests; centralizes expected offset/size data structures.

Risks and test signals: `off_size::end()` assumes nonzero size. Type changes can ripple through many test vectors; compilation of block Catch2 tests is the key signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.h -->
