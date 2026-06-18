<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clean.go -->
# sources/sync-backup/git-lfs/commands/command_clean.go

Purpose: implements the Git clean filter, converting working-tree file content into a Git LFS pointer and storing the media object in local LFS storage.

Important APIs/types/functions: `clean`, `cleanCommand`, `lfs.GitFilter.Clean`, `gf.CopyCallbackFile`, `gf.ObjectPath`, `lfs.EncodePointer`, and `errors.IsCleanPointerError`. It uses `requireStdin`, `setupRepository`, `installHooks`, `tools.CopyCallback`, and Windows large-file warning helper `possiblyMalformedObjectSize`.

Control flow: `cleanCommand` requires pipe input, initializes repository and hooks, derives an optional filename argument, and calls `clean`. `clean` optionally stats the file and creates a progress callback, delegates transformation to `GitFilter.Clean`, handles already-clean pointer errors by writing the original pointer bytes, moves the cleaned temp object into the media store if no matching object exists, validates size mismatches for non-extension objects, and writes the pointer to Git.

State and persistence behavior: stores content-addressed media files under `.git/lfs/objects`, removes ownership from temporary clean files via `Teardown`, writes pointer text to stdout, and may leave existing objects untouched. It reads current file size to improve progress and pointer metadata.

Dependencies/integration points: clean is shared by filter-process, migrate import, merge-driver output, and pointer generation behavior. It depends on configured LFS extensions, object path layout, and central command error handling.

Risks and test signals: risks include fatal exits inside a helper used by multiple commands, mismatch handling when extensions are present, rename failures across filesystems, and Windows files larger than 4 GiB warning paths. Test signals include idempotent cleaning of an existing pointer, media-object creation, duplicate object reuse, extension-enabled clean, stdin filter invocation, and size mismatch protection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_clean.go -->
