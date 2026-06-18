<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/create_test.sh -->
# sources/storage-engines/wiredtiger/test/catch2/create_test.sh

Purpose: Developer script to create boilerplate Catch2 unit test files and insert them into `test/catch2/CMakeLists.txt`.

Important APIs/types/functions: Parses optional `-m module`, validates test name with `[a-z][_a-z0-9]+`, writes a C++ template including `wt_internal.h` and mock session helper, sorts existing test file entries, inserts a new CMake source line with `sed`, and runs `dist/s_all`.

Control flow: Fails on bad argument counts, invalid names, or existing files; otherwise creates the file under `tests` or `tests/<module>`, updates CMake, runs style/all-generation script, and prints manual next steps.

State and persistence behavior: Creates a `.cpp` test file and modifies `CMakeLists.txt`; runs repository maintenance script.

Dependencies and integration points: Depends on Bash, `sed`, `grep`, sorted shell arrays, and WiredTiger `dist/s_all`.

Risks and test signals: Uses `echo >` and `sed -i`, so failed insertion can partially modify files. Run from the expected directory and inspect CMake diff afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/create_test.sh -->
