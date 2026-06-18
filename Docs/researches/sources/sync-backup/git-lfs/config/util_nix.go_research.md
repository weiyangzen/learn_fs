<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_nix.go -->
# sources/sync-backup/git-lfs/config/util_nix.go

## Research

This Unix-only file provides `umask()` for permission calculations. It calls `syscall.Umask(022)` to retrieve the current process mask, immediately restores the original value, and returns it.

The function integrates with `Configuration.getMask` and repository file/directory permission decisions. Its side effect is process-global but brief; concurrent code changing umask could race because POSIX umask is process-wide. Tests in `config_test.go` use this helper indirectly when computing expected defaults. The platform split pairs with `util_windows.go`, where no syscall exists.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_nix.go -->
