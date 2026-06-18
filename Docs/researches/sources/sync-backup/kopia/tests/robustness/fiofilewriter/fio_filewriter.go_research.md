<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/fiofilewriter/fio_filewriter.go -->
# sources/sync-backup/kopia/tests/robustness/fiofilewriter/fio_filewriter.go

This file implements `robustness.FileWriter` using `tests/tools/fio.Runner`. It defines option keys for directory depth, file sizes, file counts, dedupe percentage, delete percentage, free-space limits, and per-action I/O limits, plus defaults for randomized robustness workloads.

`New` constructs a FIO runner. `WriteRandomFiles` chooses a random depth, file-size range, file count, dedupe percentage, and optional I/O limit, checks free space with `syscall.Statfs`, builds `fio.Options`, logs effective parameters, and delegates to `WriteFilesAtDepthRandomBranch`. Delete methods choose depths and delegate to `DeleteDirAtDepth` or `DeleteContentsAtDepth`, translating `fio.ErrNoDirFound` into `robustness.ErrNoOp`; `DeleteEverything` performs a 100% root-content delete.

State lives in the embedded runner and its temp data directory. Dependencies are FIO, Docker/local FIO environment variables, `maps`, `math/rand`, and robustness sentinels. Risks include invalid option ranges causing `rand.Intn` panics, integer narrowing for large sizes, platform-specific `Statfs`, and destructive deletes if runner roots are wrong. Tests exercise the lower FIO workload layer; robustness tests validate integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/fiofilewriter/fio_filewriter.go -->
