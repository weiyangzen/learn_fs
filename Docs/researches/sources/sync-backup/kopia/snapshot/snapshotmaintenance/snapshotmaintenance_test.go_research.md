# sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance_test.go

Purpose: format-parametrized integration tests for snapshot maintenance, snapshot GC safety, auto-maintenance liveness, and read-only rejection.

Important APIs/types/functions: `testHarness`, `TestSnapshotGCSimple`, `TestMaintenanceReuseDirManifest`, `TestSnapshotGCMinContentAgeSafety`, `TestMaintenanceAutoLiveness`, `TestNoMaintenanceReadOnly`, plus helpers for fake time, snapshots, flushing, raw object creation, and content deletion checks.

Control flow: tests create mock filesystem snapshots, delete manifests, advance fake time past or near safety windows, run full/auto maintenance, verify content deletion/undeletion, simulate concurrent reuse of directory manifests, and ensure auto maintenance keeps task runs recent over 21 days.

State and persistence: heavily mutates test repositories: manifests, content objects, deleted flags, maintenance schedules, and direct writer sessions.

Dependencies and integration points: covers snapshot maintenance wrapper, snapshot GC, generic repository maintenance, faketime, repotesting, uploader, object/content APIs, and format versions.

Risks and test signals: timing safety uses fake time and a 20-second buffer around `MinContentAgeSubjectToGC`. Reuse test checks that referenced content can be undeleted by a later maintenance run. Read-only test expects `ErrReadonly`.
