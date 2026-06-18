# sources/sync-backup/kopia/snapshot/upload/estimate_test.go

Purpose: regression test that upload estimation does not consume streaming directories.

Important APIs/types/functions: `fakeProgress`, `TestEstimate_SkipsStreamingDirectory`, `virtualfs.NewStreamingDirectory`, `policy.BuildTree`, and `upload.Estimate`.

Control flow: the test creates a virtual root containing a streaming directory with one file, runs estimate with the default policy tree, and verifies final stats through `fakeProgress.Stats`.

State and persistence: all filesystem entries are virtual/mock in-memory objects; no repository is used.

Dependencies and integration points: protects `estimate` behavior for directories where `SupportsMultipleIterations` is false, which prevents destructive or one-shot iteration during estimation.

Risks and test signals: only final callback assertions are checked. Expected result is zero files, two directories, and zero errors, proving the streaming child file was not traversed.
