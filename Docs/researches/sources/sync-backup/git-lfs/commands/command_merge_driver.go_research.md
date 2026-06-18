<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_merge_driver.go -->
# sources/sync-backup/git-lfs/commands/command_merge_driver.go

Purpose: implements a custom merge driver that smudges LFS pointer inputs to real file contents, runs a merge program, then cleans the merged output back into an LFS pointer.

Important APIs/types/functions: globals for `mergeDriverAncestor`, `mergeDriverCurrent`, `mergeDriverOther`, `mergeDriverOutput`, `mergeDriverProgram`, `mergeDriverMarkerSize`; `mergeDriverCommand`, `processFiles`, `mergeCleanup`, and `mergeProcessInput`.

Control flow: validates mandatory file arguments, creates temp files for ancestor/current/other/output, converts input pointers to content via `GitFilter.Smudge` or copies non-pointer content, formats a merge command with percent substitutions, runs it through `sh -c`, captures conflict exit status, opens the temporary merged file, cleans it into the requested output pointer file, removes temps, and exits with the merge status.

State and persistence behavior: creates temporary files, downloads LFS objects if needed for smudging, writes the final cleaned pointer to `--output`, and stores merged media in the local LFS object cache through `clean`.

Dependencies/integration points: integrates Git merge-driver configuration, `git merge-file` default program, subprocess percent substitution, LFS pointer decoding, transfer manifest downloads, and clean filter storage.

Risks and test signals: risks include shell command injection if configured program is unsafe, temp cleanup only for expected specifier keys, missing error check after smudge in `mergeProcessInput`, and output mode fixed at 0600. Test signals include pointer-pointer merge, non-pointer input fallback, custom merge program, conflict exit propagation, missing pointer download, and cleanup after failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_merge_driver.go -->
