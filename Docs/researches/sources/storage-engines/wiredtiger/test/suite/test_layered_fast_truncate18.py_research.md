<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate18.py

Purpose: tests write conflict detection for overlapping follower fast-truncate operations.

Important APIs/types/functions: uses `closing`, `nullcontext`, `WiredTigerError`, shared mixin helpers, and local explicit-session helpers `cursor_on`, `auto_closing_session`, `cursor_for_key`, and `truncate_on`. The expected conflict message is `/conflict between concurrent operations/`.

Control flow: tests start from a 1-100 stable follower dataset. They verify multiple truncates in the same transaction do not self-conflict; overlapping uncommitted truncates from another session conflict with and without ingest keys; non-overlapping truncates commit; a rolled-back truncate leaves no residual conflict; an invisible committed truncate still conflicts for a reader at an older timestamp; and a visible committed truncate does not conflict for a later read timestamp.

State and persistence behavior: truncate entries carry transactional visibility and conflict metadata beyond simple read visibility. A truncate invisible to a transaction can still cause write conflict if overlapping.

Dependencies/integration points: integrates WT rollback/conflict detection, timestamped transactions, and layered truncate list bookkeeping. Risks are leaks from hand-managed transactions if a failure path changes. Test signals are expected exceptions or successful commit paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate18.py -->
