# sources/object-store/minio/cmd/data-scanner.go

## Purpose
`data-scanner.go` implements MinIO's background namespace scanner. It elects one cluster scanner, advances persisted scan cycles, scans disk folders into data-usage caches, applies lifecycle actions, queues healing and replication repair, detects excessive versions/folders, throttles itself dynamically, and emits scanner/audit/event metrics.

## Important APIs, Types, And Functions
`initDataScanner`, `runDataScanner`, `getCycleScanMode`, `readBackgroundHealInfo`, and `saveBackgroundHealInfo` manage cluster-level scanner scheduling and background heal mode. `scanDataFolder` and `folderScanner.scanFolder` perform recursive disk walking, cache compaction, update streaming, and abandoned-child healing checks. `scannerItem`, `sizeSummary`, `getSizeFn`, `applyHealing`, `applyActions`, `evalActionFromLifecycle`, `applyTransitionRule`, expiry helpers, `healReplication`, `dynamicSleeper`, and `auditLogLifecycle` implement object-level side effects and pacing.

## Control Flow
The scanner loop acquires `globalLeaderLock`, reads `dataUsageBloomNamePath`, waits on `scannerCycle`, starts backend usage storage, and calls `objAPI.NSScanner`. Successful cycles increment and persist `currentScannerCycle`. Folder scanning walks disk entries, skips/rescans compacted subtrees by hash/cycle, computes object sizes via injected `getSizeFn`, applies ILM/healing/replication, compacts small or overly broad subtrees, and repairs abandoned objects when erasure healing is enabled.

## State And Persistence Behavior
Persistent state includes scanner cycle data at `dataUsageBloomNamePath`, background heal info at `backgroundHealInfoPath`, and data usage caches saved by companion cache code. Runtime state includes scanner atomics from config, metrics, global heal/expiry/transition queues, events, and audit logs.

## Dependencies And Integration Points
It integrates with object layer `NSScanner`, storage disks, erasure healing, lifecycle evaluator, object lock retention, bucket versioning, replication config, expiry/transition workers, event notification, audit logging, scanner metrics, and `dataUsageCache`.

## Risks And Test Signals
Risks include complex global state, expensive scans on huge prefix trees, subtle compaction/skip behavior, lifecycle side effects during scan, and healing interactions with disk quorum. `data-scanner_test.go` covers noncurrent version expiration under replication/object-lock constraints and lifecycle delete-all/delete-marker evaluation; folder scanning and compaction need broader integration coverage.
