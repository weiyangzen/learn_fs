# sources/sync-backup/git-lfs/versioninfo.json

Purpose: Windows version resource metadata for Git LFS builds.

Important APIs/types/functions: `FixedFileInfo.FileVersion`, `StringFileInfo.FileDescription`, copyright, product name/version, and `IconPath`.

Control flow: static JSON consumed by build/resource tooling.

State and persistence: static configuration file.

Dependencies and integration points: Windows installer/resource generation references product version `3.7.0` and icon path.

Risks: version fields must stay synchronized with release metadata; stale icon path breaks resource generation.

Test signals: no tests in this subset.
