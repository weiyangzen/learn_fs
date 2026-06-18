# sources/test-tools/crashmonkey/code/user_tools/api/workload.h

Purpose: public API for deterministic workload data writes. It declares direct `pwrite` and mmap/msync helpers used by tests to write known byte patterns at specified file offsets.

Important APIs/types/functions: `int WriteData(int fd, unsigned int offset, unsigned int size)` and `int WriteDataMmap(int fd, unsigned int offset, unsigned int size)` in `fs_testing::user_tools::api`. Comments define return values as 0 on success and -1 on error.

Control flow: implementation in `src/workload.cpp` generates a 4 KiB repeated test-data block, handles unaligned starts and trailing partial pages, and either uses `pwrite` loops or mmap/memcpy/msync. State/persistence behavior: these helpers mutate an already-open file and, for mmap, explicitly call `msync(MS_SYNC)`.

Dependencies/integration: used by generated C++ workloads and WorkloadTest. Risks/test signals: offset/size are `unsigned int`, limiting very large writes; the API does not accept caller-provided data, so all tests share one deterministic pattern.
