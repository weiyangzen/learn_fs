<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/errors.go -->
# sources/sync-backup/kopia/tests/robustness/errors.go

This file centralizes sentinel errors used across the robustness framework. The sentinels distinguish expected test-control conditions (`ErrNoOp`, `ErrKeyNotFound`, `ErrInvalidOption`, `ErrCannotPerformIO`) from hard failures.

The key integration behavior is `errors.Is` matching. FIO file writers convert missing directories into `ErrNoOp`, metadata loaders treat `ErrKeyNotFound` as first-run absence, and tests intentionally mask `ErrNoOp` for delete/restore actions that cannot currently do useful work.

There is no persistence or internal control flow beyond error creation. Risks are semantic: wrapping code must preserve these sentinels, and adding new expected-action errors without using these sentinels can make randomized tests flaky. Test signals are scattered through robustness and multiclient tests that explicitly call `errors.Is` on these values.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/errors.go -->
