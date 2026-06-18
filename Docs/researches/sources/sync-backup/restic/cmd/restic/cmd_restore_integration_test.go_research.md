# sources/sync-backup/restic/cmd/restic/cmd_restore_integration_test.go

Purpose: integration tests for restore behavior, filters, latest selection, metadata handling, and layout compatibility.

Important APIs/types/functions: restore helper functions; `TestRestoreMustFailWhenUsingBothIncludesAndExcludes`; `TestRestoreIncludes`; `TestRestoreFilter`; `TestRestore`; `TestRestoreLatest`; `TestRestoreWithPermissionFailure`; `setZeroModTime`; `TestRestoreNoMetadataOnIgnoredIntermediateDirs`; `TestRestoreDefaultLayout`.

Control flow and state: tests create repositories and files, back up fixture data, restore into temp targets, then inspect filesystem sizes/existence/diffs. Include/exclude tests exercise inline and file-based patterns. Latest tests create multiple snapshots with different paths. Metadata test checks filtered intermediate directories do not get original metadata unless selected.

Dependencies and integration points: uses backup/check/list helpers, directory diff helpers, random data appending, syscall utimes, and fixture repos.

Risks: filesystem metadata tests can be OS-sensitive. Permission failure fixture assumes expected behavior of restore error handling.

Test signals: broad coverage for restore selection, output filesystem correctness, filter validation, and compatibility with older default layout repos.
