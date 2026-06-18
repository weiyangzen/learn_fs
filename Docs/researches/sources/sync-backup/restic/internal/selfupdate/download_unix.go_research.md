<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_unix.go -->
# sources/sync-backup/restic/internal/selfupdate/download_unix.go

## Purpose
Provides Unix self-update removal behavior.

## Important APIs and Control Flow
`removeResticBinary` is a no-op because POSIX systems can rename over an executing binary after the replacement file is ready. Control flow simply returns nil.

## State, Persistence, Dependencies, and Integration
No state is changed in this shim; replacement state is handled by `os.Rename` in `extractToFile`.

## Risks and Test Signals
Risk is platform assumption drift on unusual Unix filesystems, but this is the standard update path for POSIX.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_unix.go -->
