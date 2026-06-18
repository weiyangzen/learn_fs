<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovfuzzer/kcovfuzzer.c -->
# sources/test-tools/syzkaller/tools/kcovfuzzer/kcovfuzzer.c

## Purpose

LibFuzzer bridge that feeds kernel interfaces while converting KCOV PCs into libFuzzer counters.

## Important APIs, Types, and Functions

`LLVMFuzzerTestOneInput`, fuzz targets `bpf`, `trace_filter`, `binfmt`, KCOV `init`, `cover_start/stop`, `/dev/kmsg` input logging.

## Control Flow

First input selects target from `KCOVFUZZER`, initializes KCOV, then each iteration logs input, exercises subsystem under coverage, hashes PCs into `__libfuzzer_extra_counters`.

## State and Persistence Behavior

Global target function/KCOV buffer and persistent fds; writes kernel control files and kmsg.

## Dependencies and Integration Points

Requires Linux root/debugfs, KCOV, libFuzzer, and enabled BPF/tracing/binfmt_misc.

## Risks and Edge Cases

Can destabilize host kernel state; `KCOVFUZZER` is not null-checked; static builds need sanitizer signal options.

## Test Signals

Run each mode in an isolated VM with bounded corpus and check counters change.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovfuzzer/kcovfuzzer.c -->
