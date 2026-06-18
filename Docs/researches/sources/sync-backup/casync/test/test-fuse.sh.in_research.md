# sources/sync-backup/casync/test/test-fuse.sh.in

Purpose: integration test for FUSE mounting of a casync index.

Important APIs/types/functions: creates a scratch source copy, computes digest, makes `.caidx`, extracts it, optionally loads FUSE and launches `casync mount` via `notify-wait`, then compares mounted digest.

Control flow/state: mutates scratch directory and optionally creates a live mount that is killed/unmounted at the end.

Dependencies/integration: requires built casync/notify-wait, FUSE support, `/dev/fuse`, and root for module loading in some environments.

Risks/test signals: environment-sensitive but valuable for mounted read path correctness. Cleanup must handle failed mount/kill paths carefully.

Source research group: `subset-b-009122`.
