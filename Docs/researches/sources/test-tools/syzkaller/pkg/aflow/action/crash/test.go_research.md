# sources/test-tools/syzkaller/pkg/aflow/action/crash/test.go

## Purpose

`test.go` implements the `TestPatch` action used by patch generation loops. It formats and captures the current kernel source diff, builds the modified kernel, runs the reproducer on it, returns build/boot/crash errors as `TestError`, and restores the scratch source tree afterward.

## Important APIs, Types, and Functions

`TestPatch = aflow.NewFuncAction("test-patch", testPatch)`. `testArgs` carries kernel, VM, repro, and scratch source configuration; `testResult` returns `PatchDiff` and `TestError`. Supporting functions are `testPatchBuild`, `testPatchRepro`, `currentDiff`, `undoChanges`, and `findClangFormatDiff`.

## Control Flow

`testPatch` defers `undoChanges`, computes the formatted current diff, short-circuits with `No patch to test.` when empty, builds a cache key from kernel/image/VM/repro/patch hashes, and caches the sequence of build then repro test. Build errors are converted into `TestError` strings rather than hard errors. Repro testing rejects non-Linux targets as flow errors, runs `RunTest`, and returns the crash report if the bug still reproduces or the boot error otherwise. `currentDiff` marks untracked files intent-to-add, runs `git diff -U0`, pipes it through the newest `clang-format-diff.py`, then returns a full `git diff`.

## State and Persistence Behavior

The scratch repository is intentionally mutated by code-editing tools before this action. `testPatch` always attempts to reset tracked changes and clean untracked files afterward, while keeping ignored build artifacts for speed. Patch test results are cached under `patch-test` using patch and environment hashes.

## Dependencies and Integration Points

It depends on kernel building (`kernel.BuildKernel`), crash testing (`RunTest`), `osutil` command helpers, `hash`, `targets`, and system `git` plus `clang-format-diff.py`. It is the validation gate inside patch generation and patch iteration loops.

## Risks and Edge Cases

`undoChanges` is destructive to scratch-tree edits by design; it must never point at a non-scratch user checkout. Formatting requires distro-specific `clang-format-diff.py` paths. The cache key omits `ReproSyz` and `ReproOpts`, so if only those change while C repro and other fields stay fixed, cache reuse could be surprising. Build failures are currently classified as patch errors, with a TODO about infra-vs-patch distinction.

## Test Signals

No direct unit tests are included. Workflow tests indirectly verify registration, but real confidence requires integration with a scratch git tree, clang-format, kernel build, and VM repro run.
