<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/stress_test/stress_test.go -->
# sources/sync-backup/kopia/tests/stress_test/stress_test.go

This file stress-tests Kopia content write/read behavior under concurrent managers. `TestStressBlockManager` is gated by `KOPIA_STRESS_TEST` and short mode, creates in-memory blob storage, configures content format options, and runs workers for 3 seconds locally or 30 seconds in CI.

`stressTestWithStorage` starts 16 parallel subtests. Each `stressWorker` repeatedly writes random byte slices, occasionally flushes or closes/reopens its manager, and verifies previously written content by content ID. The worker keeps a small rolling set of blocks to read back.

State is in-memory blob storage shared across workers plus per-worker write managers and random seeds. Dependencies include content manager internals, `blobtesting`, `format`, `encryption`, and `gather`. Risks include nondeterministic failure reproduction, hidden races only surfacing under stress, and runtime scaling in CI. Test signal is explicit but opt-in.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/stress_test/stress_test.go -->
