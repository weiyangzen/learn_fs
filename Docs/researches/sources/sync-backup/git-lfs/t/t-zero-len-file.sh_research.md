<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-zero-len-file.sh -->
# sources/sync-backup/git-lfs/t/t-zero-len-file.sh

Purpose: verifies zero-length LFS files can be pushed and pulled correctly.

Important APIs/functions: uses `git lfs track`, zero-byte file creation, push/pull or clone operations, and object assertions.

Control flow: one case commits and pushes a zero-length tracked file; another pulls or checks out the zero-length file and verifies it remains empty rather than missing or pointer text.

State and persistence: stores an LFS pointer with size 0, local object metadata, and remote object storage.

Dependencies and integration points: integrates with clean/smudge filters, pointer size handling, transfer upload/download, and filesystem zero-byte files.

Risks: zero-byte content can be confused with missing files or empty pointer reads, leading to skipped uploads/downloads.

Test signals: two cases cover push and pull of zero-length files.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-zero-len-file.sh -->
