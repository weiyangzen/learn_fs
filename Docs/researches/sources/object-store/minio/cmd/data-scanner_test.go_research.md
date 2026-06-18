# sources/object-store/minio/cmd/data-scanner_test.go

## Purpose
`data-scanner_test.go` validates lifecycle decisions made by scanner item processing, especially around noncurrent-version expiration, object lock retention, replication purge state, and delete-all/delete-marker lifecycle actions.

## Important APIs, Types, And Functions
`TestApplyNewerNoncurrentVersionsLimit` sets up erasure storage, bucket metadata, lifecycle/versioning config, expiry workers, `scannerItem.applyActions`, and an accounting callback. `TestEvalActionFromLifecycle` calls `evalActionFromLifecycle` for delete-all and delete-marker-expiration rules with and without object locking.

## Control Flow
The first test creates five synthetic object versions, varies retention metadata and replication purge status, runs `applyActions`, captures versions still counted by the accounting callback, drains expiry worker tasks, and compares expected expired versions. The second test parses lifecycle XML policies, creates current object/delete-marker `ObjectInfo`, and asserts resulting lifecycle actions.

## State And Persistence Behavior
The tests create temporary erasure disks, set global object layer and bucket metadata/versioning/expiry systems, and close worker channels. They do not persist external state.

## Dependencies And Integration Points
They integrate with lifecycle XML parsing, versioning XML, object lock, replication config, expiry worker queues, erasure test setup, and scanner accounting behavior.

## Risks And Test Signals
The tests cover key lifecycle correctness but not disk walking, cache compaction, heal queues, replication heal accounting, event/audit output, or dynamic sleeper behavior. They are strong regression signals for avoiding deletion of locked versions or versions pending replication purge.
