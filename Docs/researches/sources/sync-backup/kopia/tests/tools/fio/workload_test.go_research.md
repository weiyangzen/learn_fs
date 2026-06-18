<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload_test.go -->
# sources/sync-backup/kopia/tests/tools/fio/workload_test.go

This file tests FIO workload helpers. It verifies writing files, writing at exact depths, deleting directories at depths, and deleting contents with probabilities of none/some/all. Helper functions walk the resulting temp tree to count files/directories and assert expected outcomes.

The tests provide direct signals for the mutation behavior consumed by robustness file writers. They depend on a configured FIO runner and real filesystem effects.

Risks covered include wrong depth traversal, file count mismatch, and delete probability extremes. Residual risks include concurrency with path locks, Docker path mapping under unusual host layouts, and randomized branch choices in long robustness runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload_test.go -->
