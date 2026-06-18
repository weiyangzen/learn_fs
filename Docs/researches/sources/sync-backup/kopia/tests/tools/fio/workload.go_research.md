<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload.go -->
# sources/sync-backup/kopia/tests/tools/fio/workload.go

This file implements filesystem workload operations on top of `Runner`. It writes files at paths/depths, deletes directories, deletes probabilistic contents, traverses random existing directory trees, and creates missing branches as needed.

`WriteFiles` and depth variants lock the relevant path, create directories, translate local paths to FIO container paths, and run FIO configs. Delete methods use path locks and `operateAtDepth`, which recursively chooses shuffled directories until it finds a target or returns `ErrNoDirFound`. `writeFilesAtDepth` uses `branchDepth` to mix existing and newly-created paths. `pickRandSubdirPath` chooses a random child directory.

State is filesystem tree mutation under `Runner.LocalDataDir`; locking prevents conflicting operations when a real locker is installed. Risks include random traversal flakiness, no symlink boundary checks, deletion of root content through `DeleteContentsAtDepth`, and `rand.Intn(depth+1)` panics if callers pass negative depth. Workload tests cover writes/deletes/content deletion.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload.go -->
