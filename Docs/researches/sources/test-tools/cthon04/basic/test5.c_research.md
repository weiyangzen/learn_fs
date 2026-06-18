# sources/test-tools/cthon04/basic/test5.c

Purpose: combined write/read throughput and data integrity test for a large file.

Important APIs/types/functions: parses -h, -t, -f, -n and optionally -s when O_SYNC exists, plus size/count/fname. Uses open()/creat(), write(), read(), stat(), close(), unlink(), optional mmap/msync/munmap, MIN(), BUFSZ, DSIZE.

Control flow: enters the test directory, initializes an integer pattern buffer, writes the target file count times with truncation and size checks, opens it once to verify pattern content, then times repeated full-file reads and unlinks it.

State and persistence: creates and deletes the chosen bigfile. During execution the file is repeatedly truncated and rewritten.

Dependencies and integration points: controlled by O_SYNC, MMAP, DOSorWIN32, and tests.h DCOUNT/CHMOD_RW. It is the producer/consumer superset for test5a and test5b style workloads.

Risks: validates only complete int slots in the final partial buffer; large sizes/counts can consume substantial server I/O; O_SYNC is disabled on Windows.

Test signals: validates file size after create/write, validates read-back buffer pattern once, reports write/read rates when timing is enabled, then complete().
