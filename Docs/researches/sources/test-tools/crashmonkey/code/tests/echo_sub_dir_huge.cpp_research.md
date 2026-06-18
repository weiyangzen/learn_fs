# sources/test-tools/crashmonkey/code/tests/echo_sub_dir_huge.cpp

Purpose: stress-size version of the subdirectory echo workload. It is structured like `echo_sub_dir_big.cpp` but uses a larger `TEST_TEXT_SIZE` to pressure writeback, allocation, and recovery over a bigger file extent set.

Important APIs/types/functions: class name is still `echo_sub_dir_big` in the source, with `BaseTestCase`, `/dev/urandom`, `mkdir`, `open`, `write`, `fsync`, `stat`, `read`, and `DataTestResult`.

Control flow: setup persists the containing directory and fills a random text buffer. `run()` creates target files and writes the full huge buffer before fsync. `check_test()` stats each recovered file and reads it back for byte-for-byte comparison.

State/persistence behavior: the persisted state must include full file length and random content, not just metadata. Larger size increases exposure to delayed allocation, partial writeback, and extent recovery issues.

Dependencies/integration: direct syscall workload using `/mnt/snapshot`; expected bytes are held in the test object's memory.

Risks/test signals: memory and runtime cost are higher than the small echo test. Any partial persistence shows as wrong `st_size`, read failure, or data corruption against the random buffer.
