# sources/sync-backup/restic/cmd/restic/cmd_key_list.go

Purpose: implements `restic key list`, listing repository key metadata and identifying the active key.

Important APIs/types/functions: `runKeyList`; `listKeys`; local `keyInfo` struct with JSON fields; table output setup.

Control flow and state: command rejects arguments, opens with a read lock, then `restic.ParallelList` enumerates key files. Each key is loaded; load errors are printed and skipped. A mutex protects concurrent append to the result slice. Output is JSON array or a table with current-key marker.

Dependencies and integration points: uses `repository.LoadKey`, `restic.KeyFile`, `restic.ParallelList`, terminal/table packages, and repository connection count.

Risks: skipped load errors mean partial output can still return success. Concurrent listing yields nondeterministic key order, which tests avoid by parsing IDs.

Test signals: key integration tests rely on list output to discover removable non-current key IDs and verify command accepts no arguments.
