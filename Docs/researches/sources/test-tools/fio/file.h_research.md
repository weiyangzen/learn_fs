# sources/test-tools/fio/file.h

## Purpose
`file.h` defines fio's central file abstraction, file-related enums, flags, inline flag accessors, mount metadata, and file lifecycle function declarations. It is the contract between fio core, file setup, and ioengines.

## Important APIs, Types, And Functions
`enum fio_filetype` distinguishes regular files, block devices, character devices, pipes, and directories. `enum fio_file_flags` tracks open/closing/extend/done/size-known/hash/partial-mmap/random-map allocation state. `enum file_lock_mode`, file service selection constants, and `enum fio_fallocate_mode` define policy values used by options.

`struct fio_file` contains hash linkage, file type, descriptors/Windows handles, identity, size and offset fields, FDP/ZBD/SP-random metadata pointers, per-direction position history, first/last write ranges, engine-private `engine_pos` and `engine_data`, synchronization lock union, random map union, nonuniform distribution state, references, flags, and disk-util pointer. `FILE_FLAG_FNS` generates inline set/clear/test functions for each flag. Function declarations cover setup, open/close/size, invalidation, pre-read, add/get/put, locking, directory expansion, random maps, duplication, reset, direct I/O, and filesystem sync integration.

## Control Flow
This header has no runtime flow beyond inline flag mutation. Runtime control is implemented by file setup and ioengine code that fills `fio_file`, opens descriptors, tracks sizes, and calls generic helpers or engine-specific hooks.

## State And Persistence
`fio_file` is long-lived job state. Some fields mirror persistent target properties (`real_file_size`, device IDs), while others are transient scheduling/accounting state. `engine_data` and `engine_pos` are intentionally reserved for ioengines.

## Dependencies And Integration Points
The header depends on fio compiler annotations, data direction types, intrusive lists, random distribution libraries, axmap, LFSR, and optional `CONFIG_SYNCFS`. Nearly every ioengine in this subset uses `fio_file` descriptors, file names, file sizes, `engine_pos`, or `engine_data`.

## Risks
Because `fio_file` is shared across many subsystems, flag misuse can create cross-module bugs. The union fields require callers to know which mode owns them. Engine-private fields can conflict if layered functionality assumes ownership. Reference and lock lifetimes must match file setup/teardown exactly.

## Test Signals
Tests should validate flag helpers, generic open/close/size implementations, add/get/put reference behavior, lock/unlock integration, random-map initialization, ZBD/FDP metadata lifetimes, and ioengine use of `engine_data`/`engine_pos`.
