## sources/storage-engines/pebble/tool/db_analyze_data_test.go

Purpose: provides a focused smoke test for `fileSet` weighted sampling used by `db analyze-data`.

Important APIs/types/functions: `TestFileSetSampling` creates one large `.sst` and ten tiny `.sst` files in a memfs, repeatedly builds a `fileSet`, samples the first file, and asserts the small-file selection rate is less than ten times the theoretical probability. `fsWrapper.Stat` and `fileInfoWrapper.ModTime` make memfs files appear one hour old so `vfsStorage.Size` does not reject them as still-being-written.

Control flow: each iteration constructs `newVFSStorage(fsWrapper{memFS}, "")`, calls `makeFileSet`, samples once, and counts whether the chosen filename differs from the large file. The assertion uses the expected size-weighted probability and a generous bound explained by the Chernoff comment.

State and persistence: all files are in-memory and rebuilt once before the loop. Randomness uses `math/rand/v2` PCG seeded with random seeds, so the test is probabilistic but has an extremely low false-failure bound under the stated distribution.

Dependencies and integration: depends on `vfs.MemFS`, Pebble filename formatting via `base.DiskFileNum`, and `testify/require`. It directly exercises the storage abstraction and sampling logic, not the full Cobra command or compression analyzer.

Risks: because the test uses random seeds, it is not perfectly deterministic. It does not test refresh preservation, CSV writing, remote sampling, timeouts, read limiting, or analyzer errors. It assumes the first `Sample` is the behavior most relevant to weighted ordering.

Test signals: catches regressions that make sampling uniform or otherwise insensitive to file size. The ModTime wrapper also documents the production 15-second young-file guard.
