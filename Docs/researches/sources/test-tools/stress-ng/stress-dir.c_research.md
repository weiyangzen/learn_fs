# sources/test-tools/stress-ng/stress-dir.c

Purpose: implements the `dir` filesystem stressor, creating, reading, renaming, and deleting many directories under a stress-ng temporary directory while exercising directory-specific error paths.

Important APIs/types/functions: `stress_dir_sync()`, `stress_dir_flock()`, `stress_dir_truncate()`, and `stress_dir_mmap()` probe directory fd behavior. `stress_dir_read()` opens/stat entries. `stress_dir_rename()` renames each child out and back to exercise directory iteration under mutation. `stress_mkdir()` alternates between `mkdir()` and `mkdirat()`. `stress_invalid_mkdir*()` and `stress_invalid_rmdir()` exercise expected failure paths. `stress_dir_readdir()` verifies `rewinddir()` sees files created after `opendir()`. `stress_dir()` owns the main loop.

Control flow: the stressor creates a temp directory, optionally opens it with `O_DIRECTORY`, forks a concurrent reader, then loops. Each iteration mmaps/flocks/truncates the directory, creates `dir-dirs` children using gray-code filenames, runs invalid mkdir/rmdir cases, reads and renames entries, verifies readdir/rewinddir behavior, removes created directories, fsyncs/syncs, and increments bogo counts. On stop, it tidies partial work and kills the reader child.

State and persistence behavior: all persistent filesystem effects are confined to the stress-ng temp directory and removed with `stress_dir_tidy()` plus `stress_fs_temp_dir_rm_args()`. Runtime counters are local. The forked reader does not share explicit state beyond the directory contents.

Dependencies and integration points: uses stress-ng filesystem naming/temp helpers, `core-killpid`, `stress_sync_start_wait`, and option `dir-dirs` bounded from 64 to 65536. Registered as `stress_dir_info`, classifier `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: filesystem-specific behavior around directory mmap/truncate/ftruncate, concurrent readdir under rename, and `d_reclen` can differ by platform. High `dir-dirs` values can hit `ENOSPC`, `ENOMEM`, or `EMLINK`, which are treated as expected capacity limits. Cleanup must handle partial creation when stop arrives.

Test signals: run with minimized/maximized `dir-dirs`, short timeout, and `--verify`; confirm no leftover temp directories, no zero-sized dirent failures, and no unexpected rename/readdir verification failures.
