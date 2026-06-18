# sources/storage-engines/wiredtiger/test/suite/test_layered_schema07.py

## Purpose

This suite tests `WT_SESSION::publish` for disaggregated schema operations on leaders. It verifies that create and drop operations are not included in checkpoints until published with a schema epoch and that checkpoint processing respects the stable disaggregated schema epoch.

## Important APIs, Types, and Functions

Helpers set stable schema epochs, run timestamped leader checkpoints, open followers, check follower table visibility after checkpoint pickup, call `session.publish`, and poll statistics. It uses `suite_subprocess` for expected panic cases and statistics such as `session_table_publish_success`, `session_table_publish_fail`, `checkpoint_disagg_metadata_unstable`, and `checkpoint_disagg_metadata_apply`.

## Control Flow

Functional tests show create is invisible before publish and visible after publish plus checkpoint, and drop is deferred until the drop is published. Error tests reject zero epochs, epochs not newer than the current stable schema epoch, and unsupported URI types. Two subprocess tests intentionally panic by checkpointing dirty table data when the required CREATE metadata is unpublished or published at an epoch later than the stable epoch. The stats test verifies success/failure publish counters and checkpoint apply/defer counters.

## State, Persistence, and Dependencies

State includes the metadata operation queue, stable schema epoch, transactional timestamps, shared metadata, follower checkpoint pickup, and connection statistics. Dependencies include `os`, `time`, `wiredtiger`, `wttest`, `helper_disagg`, `suite_subprocess`, `wtscenario`, and `wiredtiger.stat`.

## Risks and Test Signals

Risks include exposing unpublished schema to followers, applying drops too early, allowing invalid publish epochs, skipping required panic paths, or miscounting stats. Signals combine follower visibility checks, precise error-message assertions, subprocess nonzero return codes, and retrying statistic equality.
