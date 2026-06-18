## sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target_test.go

This file tests fuzz-target selection and merge behavior. `TestSelectFuzzConfigs` verifies single Cc match, multiple Cc matches, and default fallback. `TestMergeKernelFuzzConfigs` verifies distinct kernel configs/tracks stay split while compatible configs merge. `TestMergeFuzzConfigs` verifies focus/corpus deduplication, skip-cover OR behavior, and bug-title regexp propagation.

The test signals are focused on pure functions and avoid external state. They do not cover case normalization mismatches for configured email lists, empty config input, or order behavior across grouped keys beyond the explicit examples.
