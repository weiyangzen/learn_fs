# sources/sync-backup/kopia/repo/maintenance/maintenance_run_test.go

Purpose: unit tests maintenance scheduling decisions for orphaned pack deletion, content rewrite gating, and safe deleted-content drop times.

Important APIs/types/functions: `TestShouldDeleteOrphanedBlobs`, `TestShouldRewriteContents`, `TestFindSafeDropTime`, shared test timestamps, `shouldDeleteOrphanedPacks`, `shouldQuickRewriteContents`, `shouldFullRewriteContents`, and `findSafeDropTime`.

Control flow: table-driven cases build synthetic `Schedule.Runs` histories and safety parameters, then assert boolean decisions or cutoff timestamps.

State/persistence behavior: no repository state; tests exercise pure scheduling logic.

Dependencies/integration: uses package-internal access because tests are in package `maintenance`.

Risks/test signals: protects the most safety-critical timing logic without needing slow integration tests. It cannot catch content-manager side effects.
