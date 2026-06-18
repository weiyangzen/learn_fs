# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.8.in

## Role

Manual page for `ntfscmp`, a utility for comparing two NTFS filesystems or image files.

## Documented Interface

Documents `--no-progress-bar`, `--verbose`, and `--help`, plus exit status. It positions the utility primarily as a development/verification tool for identifying metadata differences.

## Important Behavior

The page recommends comparing metadata images produced by `ntfsclone --metadata` when ordinary timestamp churn is not interesting.

## Research Notes

The manpage matches the implementation’s terse difference reporting and progress-bar behavior.
