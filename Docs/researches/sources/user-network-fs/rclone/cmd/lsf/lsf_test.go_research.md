# sources/user-network-fs/rclone/cmd/lsf/lsf_test.go

Purpose: unit-tests `Lsf` formatting behavior against local `testfiles`.

Important tests: `TestDefaultLsf`, `TestRecurseFlag`, `TestDirSlashFlag`, `TestFormat`, `TestSeparator`, `TestWholeLsf`, `TestTimeFormat`, and `TestTimeFormatMax`. They compare exact output strings and derive expected modtimes from `list.DirSorted` when timestamps are involved.

Control flow/state: tests initialize rclone test config, create a local Fs, mutate package globals for flags, call `Lsf` into a buffer, and then manually reset globals. Persistence is limited to fixture reads.

Dependencies/integration: local backend import, `fstest`, `fs.NewFs`, `list`, `operations.FormatForLSFPrecision`, testify. Risks: manual global cleanup is easy to miss and can make tests order-sensitive; exact fixture ordering depends on list sorting. Coverage is strong for the public helper but not command flag parsing.
