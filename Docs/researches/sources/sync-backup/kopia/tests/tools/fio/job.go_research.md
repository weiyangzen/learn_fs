<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/job.go -->
# sources/sync-backup/kopia/tests/tools/fio/job.go

This file defines a single FIO job. `Job` has a `Name` and `Options`; `Job.String` renders a fio config section with `[name]` followed by option lines.

The type is used inside `Config` for debug/log formatting and by `Runner.argsFromConfigs` to produce CLI flags. Option ordering is map-based, so string output order is nondeterministic unless tests account for it.

There is no state. Risks are formatting nondeterminism and divergence between string representation and CLI argument generation. FIO tests provide signals around job/config output and execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/job.go -->
