<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_test.h -->
# sources/test-tools/syzkaller/executor/common_test.h

## Purpose

`common_test.h` is the executor/csource support layer for syzkaller's synthetic test OS target. It implements deterministic pseudo-syscalls used by executor tests and fuzzer tests rather than real kernel-environment setup. The file focuses on simple memory mapping, errno shaping, comparisons, controlled crashes, coverage injection hooks, and no-op feature setup.

## Important APIs, Types, And Functions

- `syz_mmap()` maps a fixed anonymous private writable mapping at a requested address and length.
- `syz_errno()` sets `errno` to the provided value and returns `0` for zero or `-1` otherwise.
- `syz_exit()` exits through the executor-provided `doexit()`.
- `syz_sleep_ms()` delegates to the common `sleep_ms()` helper.
- `syz_compare()` checks byte-for-byte equality between expected and actual buffers, sets `EBADF` on length mismatch and `EINVAL` on content mismatch, and dumps both buffers on error.
- `syz_compare_int()` accepts a count from 2 to 4 and compares a vararg set of integer values while checking unused arguments are zero.
- `syz_compare_zlib()` decompresses a generated zlib image into `./uncompressed`, mmaps the result if non-empty, and compares it through `syz_compare()`.
- `do_sandbox_none()` rejects unsupported net injection and devlink PCI feature combinations for the test OS, then enters `loop()`.
- `fake_crash()` and `syz_test_fuzzer1()` produce named synthetic crashes for specific argument triples.
- `syz_inject_cover()` and `syz_inject_remote_cover()` are declarations in executor builds, with csource stubs returning `0`.
- `setup_sysctl()` and `setup_cgroups()` are no-op placeholders.

## Control Flow

Most pseudo-syscalls return immediately after performing one deterministic action. Comparison helpers branch to a shared error path that logs buffer contents before returning `-1`.

`do_sandbox_none()` is the only sandbox entry. It deliberately fails if net injection is requested and exits with a feature message if devlink PCI is requested. Otherwise it calls the generated `loop()` directly.

`syz_test_fuzzer1()` implements two reproducible crash triggers: `(1, 1, 1)` and `(1, 2, 3)`. Both call `fake_crash()`, which emits a `failmsg()` formatted with `{{CRASH: ...}}` and exits.

## State And Persistence Behavior

The file has almost no durable state. `syz_errno()` intentionally mutates thread/process `errno`; `syz_compare_zlib()` creates `./uncompressed` with `O_EXCL` and leaves normal file lifetime to the surrounding executor/test cleanup; `syz_mmap()` mutates the process address space. Coverage injection hooks may affect executor coverage state when linked with `executor_test.h`, but the csource stubs do not.

## Dependencies And Integration Points

The file uses common executor facilities such as `doexit`, `sleep_ms`, `debug`, `debug_dump_data`, `fail`, `failmsg`, `exitf`, feature flags, and `loop()`. zlib comparison depends on `common_zlib.h` and `puff_zlib_to_file()`.

The synthetic crash strings are intended for syzkaller report detection and fuzzer tests. `syz_inject_cover` and `syz_inject_remote_cover` are resolved by executor test-specific code in executor builds.

## Risks And Edge Cases

- `syz_compare_zlib()` returns `-1` without closing/unmapping on several error paths; this is acceptable in short-lived tests but should not be used as a long-running library pattern.
- `syz_compare_int()` reads four varargs regardless of `n`; callers must pass the full generated signature.
- `syz_mmap()` uses `MAP_FIXED`, so it can replace existing mappings in the test process.
- `syz_compare()` dumps arbitrary input buffers on mismatch, which is useful for tests but can produce large logs if lengths are large.
- `do_sandbox_none()` intentionally rejects features rather than trying to emulate them, so feature-detection tests should expect failure messages.

## Test Signals

- Unit-style generated programs can assert return values and `errno` from `syz_errno`, `syz_compare`, and `syz_compare_int`.
- Synthetic crash detection should classify the two `syz_test_fuzzer1()` argument triples as distinct named crashes.
- Coverage tests should link executor definitions for `syz_inject_cover` and `syz_inject_remote_cover`; csource mode should see harmless `0` returns.
- zlib comparison tests can check that decompressed bytes match and mismatches set the expected comparison errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_test.h -->
