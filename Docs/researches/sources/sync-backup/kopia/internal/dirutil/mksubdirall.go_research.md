# sources/sync-backup/kopia/internal/dirutil/mksubdirall.go

Purpose: safely creates subdirectories under an existing top-level directory without recreating the top-level directory if it is missing or unmounted.

Important APIs/types/functions: `ErrTopLevelDirectoryNotFound`, `OSInterface`, `MkSubdirAll`, `trimTrailingSeparator`, and `getParent`.

Control flow: trims trailing separators, rejects `subDir` paths not longer than `topLevelDir`, tries to `Mkdir(subDir)`, recursively creates the parent only on `IsNotExist`, retries, and treats success or `IsExist` as success.

State and persistence behavior: persistent effect is directory creation below the top-level path. It deliberately refuses to create the top-level directory itself.

Dependencies/integration: abstraction over OS calls enables tests and portability.

Risks/test signals: it compares path strings by length/prefix shape rather than canonical path containment, so callers must pass normalized compatible paths. Tests cover direct subdir, nested subdir, already exists, top-level rejection, and unexpected mkdir errors.
