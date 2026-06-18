# sources/storage-engines/wiredtiger/test/huge/huge.c

Purpose: standalone C test for very large WiredTiger keys and values across file/table row-store and column-store configurations. It inserts, verifies, and removes a single large item for multiple sizes.

Important APIs and functions: `CONFIG` describes URI/config/column-store key style. `lengths` spans 20 bytes, 1 MiB, 250 MiB, 1 GiB, 2 GiB, 3 GiB, and roughly 4 GiB minus 1 MiB. `run` creates the object, sets either a large key or value, commits an explicit transaction, searches back, compares with `memcmp`, removes the record, and closes the connection. `main` parses `-h` and `-s`, allocates `big`, initializes it with `a`, loops configurations and sizes, then removes the work directory.

Control flow and state: row-store configurations test both large keys and large values; column-store configurations only test large values because recno keys are scalar. Explicit transactions and cursor reset are used to avoid pinning a page that itself exceeds eviction thresholds.

Dependencies and integration: uses `test_util.h`, WiredTiger public cursor/session/connection APIs, and test allocation/removal helpers. The CMake small variant limits allocation to `SMALL_MAX` (1 MiB), despite the usage text saying "up to 1GB".

Risks and test signals: full mode is memory and disk heavy. The critical signal is exact byte equality after readback and successful removal/close. The test is sensitive to platform `size_t`, allocation limits, cache configuration, and eviction behavior for huge single updates.
