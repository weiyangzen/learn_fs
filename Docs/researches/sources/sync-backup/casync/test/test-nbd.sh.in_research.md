# sources/sync-backup/casync/test/test-nbd.sh.in

Purpose: integration test for NBD device export of a casync block index.

Important APIs/types/functions: generates random blob, compares casync digest with `test-calc-digest`, creates `.caibx`, extracts with and without seed, and optionally runs `casync mkdev` through `notify-wait` to read from `/dev/nbd0`-style node.

Control flow/state: scratch files and optional kernel NBD device state are created; helper process is killed after digest comparison.

Dependencies/integration: requires NBD kernel support/root for the device portion and built helper binaries.

Risks/test signals: strong coverage for block archive extraction and device serving, but often skipped or partial in unprivileged CI.

Source research group: `subset-b-009122`.
