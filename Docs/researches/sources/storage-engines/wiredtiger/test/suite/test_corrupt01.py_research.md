<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_corrupt01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_corrupt01.py

Purpose: verifies diagnostic output when a block is corrupted, expecting block byte dumps and checkpoint extent-list context.

Important APIs and control flow: the test creates a small-page table, inserts 10000 randomly sized values, checkpoints, removes even keys to create holes, checkpoints again, closes, runs `wt verify -d dump_address` into a file, parses a row-store leaf address, overwrites that offset with `BAD_VALUE`, reopens, reads until corruption is encountered, and finally expects close to raise. It ignores expected extent-list/checksum noise.

State, persistence, and dependencies: persistent state is deliberately corrupted `.wt` file bytes and verify dump output. Dependencies include random data generation, regex address parsing, `suite_subprocess.runWt`, binary file writes, verify/read paths, and `debug_mode=(corruption_abort=false)`.

Integration points: covers block manager verification, corruption detection, verbose diagnostic plumbing, and close-time handling after corruption.

Risks and test signals: address parsing depends on dump format, and direct byte corruption is storage-layout sensitive. Disaggregated storage is skipped. Pass signals are successful corruption injection and expected `WiredTigerError` while diagnostics contain tolerated patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_corrupt01.py -->
