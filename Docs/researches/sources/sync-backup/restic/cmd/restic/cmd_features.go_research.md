# sources/sync-backup/restic/cmd/restic/cmd_features.go

Purpose: implements `restic features`, listing available feature flags and their state/default/description.

Control flow/APIs: `newFeaturesCommand` registers a no-argument advanced command. It errors if args are supplied, prints a heading, retrieves `feature.Flag.List()`, builds a table with name, type, default, and description, and writes it to terminal output.

State/persistence: read-only; feature enabling/disabling happens elsewhere through `RESTIC_FEATURES`.

Dependencies/integration: `internal/feature`, `internal/ui/table`, global terminal output, and cobra command tree. It documents runtime feature flag availability to users.

Risks/test signals: output depends on feature registry order/content. There are no local tests in this subset; compile and manual command output are the signal.
