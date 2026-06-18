# sources/user-network-fs/s3fs-fuse/src/mpu_util.h

## Purpose
Declares data structures and the public entry point for s3fs incomplete multipart upload utility mode.

## Important APIs, Types, And Functions
`INCOMP_MPU_INFO` stores one upload's `key`, `id`, and `date`. `incomp_mpu_list_t` is a vector of those records. `enum class utility_incomp_type : uint8_t` represents no utility mode, list mode, and abort mode. `extern utility_incomp_type utility_mode` is the process-global mode flag. `s3fs_utility_processing(time_t abort_time)` is the public executor.

## Control Flow
The header does not implement behavior, but it defines the mode contract consumed by option parsing and `mpu_util.cpp`. Callers set `utility_mode`, then invoke `s3fs_utility_processing()` with an abort threshold in seconds; list mode ignores the threshold and abort mode uses it.

## State And Persistence Behavior
Only `utility_mode` is declared as shared local state. Multipart upload state itself lives in S3 and is represented transiently by `INCOMP_MPU_INFO` values. No local persistence is declared.

## Dependencies And Integration Points
The header depends on standard `cstdint`, `ctime`, `string`, and `vector`. It is integrated with command-line utility processing, S3 XML parsing that fills `incomp_mpu_list_t`, and request code that aborts multipart upload IDs.

## Risks
The global mode flag is not thread-local or synchronized; utility mode should remain one-shot/single-threaded. `INCOMP_MPU_INFO::date` is a string rather than a parsed time, so malformed date handling is deferred until abort processing. The enum values are simple but should stay aligned with command-line parser expectations.

## Test Signals
Compile tests should verify enum usage and linkage of `utility_mode`. Behavioral tests in `mpu_util.cpp` should create representative `incomp_mpu_list_t` records, including invalid dates and duplicate keys with different upload IDs.
