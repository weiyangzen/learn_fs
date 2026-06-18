# sources/sync-backup/git-lfs/tools/util_darwin_test.go

Purpose: macOS-specific tests for clonefile helpers.

Important APIs/types/functions: `TestCheckCloneFileSupported`, `TestCloneFile`, and `TestCloneFileByPath`.

Control flow: probes temp dir support, asserts generic `CloneFile` is unsupported without error, and clones a written temp source to a destination when platform/filesystem supports it.

State and persistence: writes temp files in `os.TempDir`; skips when clonefile is unsupported.

Dependencies and integration points: validates Darwin implementation used by copy optimization.

Risks: platform and filesystem dependent; temp file names are fixed (`src`, `dst`) and could collide in unusual concurrent runs.

Test signals: direct coverage of Darwin clone behavior, with skip paths for unsupported environments.
