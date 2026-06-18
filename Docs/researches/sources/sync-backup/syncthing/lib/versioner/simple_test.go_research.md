# sources/sync-backup/syncthing/lib/versioner/simple_test.go

Purpose: tests version filename tagging, simple retention, path expansion, and archive-directory permission helper behavior.

Important tests: `TestTaggedFilename` validates tag insertion before extensions and tag extraction across names containing tildes. `TestSimpleVersioningVersionCount` archives repeatedly with keep=2 and expects only the newest two versions. `TestPathTildes` sets HOME and verifies folder/version paths beginning with `~` expand correctly. `TestArchiveFoldersCreationPermission` checks version directory tree permissions mirror source directories and remain stable across repeated archive. `TestDupDirTreeWritePermissions` and `TestDupDirFastPath` validate helper behavior that creates/upgrades destination directory permissions with user-write bits.

State and persistence: temp directories, fake filesystems, and package `testdata` cleanup.

Dependencies and integration: covers simple versioner plus shared helper functions not in this specific source list.

Risks and signals: strong filesystem behavior coverage; count test is skipped in short mode. Age-based `cleanoutDays` is not tested here.
