# sources/test-tools/ior/src/utilities.c

Purpose: shared runtime utility library for IOR/mdtest/md-workbench, covering global state, memory patterns, verification, timers, MPI topology, filesystem reporting, hints, timestamps, size parsing, delays, and aligned/GPU buffers.

Important APIs and functions: exports globals declared in `utilities.h` (`rank`, `verbose`, `testComm`, output files, output format). Memory functions include `generate_memory_pattern()`, `update_write_memory_pattern()`, `invalidate_buffer_pattern()`, and `verify_memory_pattern()`. Timing functions include `GetTimeStamp()`, `PrintTimestamp()`, and `OpTimer*`. Topology functions include `QueryNodeMapping()`, `GetNumNodes()`, `GetNumTasks()`, and `GetNumTasksOnNode0()`. Configuration helpers include `parsePacketType()`, `updateParsedOptions()`, `SetHints()`, and `ShowHints()`. Buffer functions include `aligned_buffer_alloc()` and `aligned_buffer_free()`.

Control flow: callers initialize globals and output streams, then use these helpers during option parsing and benchmark phases. Memory-pattern generation creates deterministic rank/item signatures, while update/verify functions adjust or check per-item data. MPI helpers split or gather communicator information for placement-aware rank shifting. `OpTimer` buffers one million operation samples before flushing CSV rows.

State and persistence: owns process-wide globals and static buffers for time/human-readable strings. `OpTimer` writes CSV files. Stonewall helpers read/write a count file on rank 0 and broadcast values. Filesystem reporting writes to `out_resultfile`. Aligned allocation stores the original malloc pointer immediately before the aligned address; GPU allocations use CUDA APIs when enabled.

Dependencies and integration: used by IOR, mdtest, md-workbench, AIORI backends, and parser code. Depends on MPI, optional CUDA/GPU Direct, POSIX APIs, regex, statfs/statvfs, and project headers.

Risks: globals make behavior non-reentrant. `OpTimerInit()` compares `FILE *` with `< 0` instead of NULL. Pattern code may ignore trailing bytes smaller than 8 except for final byte checks. `StringToBytes()` supports fewer suffixes than `option.c`'s `string_to_bytes()`. `ExtractHint()` mutates input with `strtok()` and assumes valid value tokens. `ShowFileSystemSize()` divides by totals without guarding zero. `aligned_buffer_free()` treats any nonzero `ior_memory_flags` as CUDA allocation. Several functions rely on `out_logfile` being non-NULL.

Test signals: unit tests should verify size parsing, data pattern generation/verification for each packet type, aligned allocation/free under CPU and GPU builds, MPI topology helpers with fake environment variables, stonewall file broadcast, and `OpTimer` CSV output.
