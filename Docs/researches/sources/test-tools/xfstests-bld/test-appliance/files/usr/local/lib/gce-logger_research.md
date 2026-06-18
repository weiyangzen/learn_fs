# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-logger

Purpose: central status logger for GCE test VMs. It converts human status messages into VM metadata, `/var/www` status files, `/results/status`, and syslog entries.

Important flow: source `gce-funcs`; accept `--force`; invoke `run_hooks logger` unless already inside hook recursion; detect messages beginning `run xfstest`; append completed tests to `$RESULT_BASE/completed`; compute percentage from `rpt_status`, `tests-to-run`, and unique completed test names; prepend `/run/fstest-config` if present; throttle metadata updates to once per minute except for the first test or forced updates.

State and dependencies: mutates `$RESULT_BASE/completed`, `/run/last_logged`, `/var/www/statusz`, `/var/www/status`, `/results/status`, and metadata key `status`. It depends on `/root/xfstests/bin/syncfs`, `gce-add-metadata`, `logger`, shell arithmetic, and test result layout.

Integration points: LTM shard monitoring reads VM metadata status to detect progress and timeouts. The web status files expose the same status locally. Hooks can annotate or react to status changes.

Risks and test signals: progress math can divide by zero if status files are malformed, although missing files fall back to `--%`. Metadata update throttling can hide rapid state changes. Integration tests should assert metadata/status file writes and progress computation with repeated sections.
