# sources/test-tools/stress-ng/stress-rename.c

Purpose: implements the `rename` filesystem stressor, moving a temporary file back and forth across per-instance temporary directories while also exercising `renameat()` and `renameat2()` error paths when available.

Important APIs/types/functions: `stress_rename_info` registers a `CLASS_FILESYSTEM | CLASS_OS` stressor with `VERIFY_ALWAYS`. `exercise_renameat()` probes bad directory descriptors and file-descriptor-as-directory errors. `exercise_renameat2()` tests invalid flags, invalid flag combinations, `RENAME_EXCHANGE`, `RENAME_NOREPLACE`, bad descriptors, and file descriptor misuse. `stress_basename()` extracts basenames without mutating paths.

Control flow: `stress_rename()` creates two temporary directories keyed by instance, opens a temp directory fd for `*at` variants, then synchronizes. The loop creates or recreates a file, renames it to directory two and back to directory one, optionally repeats with `renameat()`, and optionally repeats with `renameat2(RENAME_NOREPLACE)`. Failures unlink both candidate names and restart with a new file.

State and persistence: state is temporary filesystem content only: two directories, one live file name, and optional directory fd. Cleanup closes fds, unlinks current candidate names, and removes both temp directories.

Dependencies and integration points: uses stress-ng temp path helpers, bad fd helper, `shim_unlink()`, `shim_fsync()`, sync, and bogo counters. `EXERCISE_RENAMEAT` depends on `HAVE_RENAMEAT` and `O_DIRECTORY`; `EXERCISE_RENAMEAT2` also depends on `HAVE_RENAMEAT2` and `RENAME_NOREPLACE`.

Risks and test signals: filesystems differ on `renameat2()` flag support and error codes. The stressor treats unexpected success on invalid combinations as verification failure. Signals are bogo increments per successful rename, complete temp cleanup, and correct handling of transient rename/open failures by restarting rather than leaking files.
