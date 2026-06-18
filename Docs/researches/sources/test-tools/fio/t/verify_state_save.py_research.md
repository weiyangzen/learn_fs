# sources/test-tools/fio/t/verify_state_save.py

## Purpose
`verify_state_save.py` provides superficial but practical regression coverage for fio's verify state persistence. It confirms that jobs can save verification state, then reload that state in verify-only and read modes across synchronous and async engines.

## Important APIs, Types, and Functions
`VerifyStateSaveTest` subclasses `FioJobCmdTest`. `setup()` builds a fio job named `verify-state` and passes through many io_uring, verification, block-size, rate, offset, directory, aux-path, and workload options when present. `check_result()` extends base validation by checking that JSON I/O counters match the expected direction set for the configured `rw`: reads only, writes only, read/write for verified writes, trim only, or trim/write.

`TEST_LIST` defines nine base random-write/random-read-write workloads over `TEST_SIZE=4M`, combining default, `verify_policy=completed`, and `verify_policy=fsynced` with optional `fsync=16` and `rwmixread=70`.

## Control Flow and State
`main()` creates an artifact root and resolves fio. For each platform-selected async and sync engine, it runs three phases. First it writes data with `verify_state_save=1`. Second it runs `verify_state_load=1` plus `verify_only=1`, pointing `directory` and `aux-path` at the saved-state phase using relative paths. Third it changes write modes to read modes and reruns state-load verification, skipping randrw cases that have no pure-read equivalent.

## Dependencies and Integration Points
It integrates with fio's JSON output, verify-state side files under job artifact directories, and `run_fio_tests()`. Platform selection maps Linux to `libaio` and `psync`, Windows to `windowsaio` and `sync`, and other platforms to `posixaio` and `psync`.

## Risks and Test Signals
Because tests mutate shared dictionaries across phases, correct removal of `verify_only`, `verify_state_load`, `directory`, and `aux-path` is essential. Relative directory computation can break if artifact layout changes. Signals are base fio exit status, JSON direction counters, and phase totals for saved, verify-only, and read verification.
