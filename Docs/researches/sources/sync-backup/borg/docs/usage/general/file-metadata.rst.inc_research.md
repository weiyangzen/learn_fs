# sources/sync-backup/borg/docs/usage/general/file-metadata.rst.inc

Purpose: documents the filesystem metadata Borg can preserve and platform support limitations.

Important APIs and control flow: covers symlinks, device/FIFO metadata, optional special-file contents via `--read-special`, hard links within an archive, nanosecond timestamps, birthtime where available, owner/group IDs and names, Unix permissions, ACLs, extended attributes, and BSD/Linux flags.

State and persistence: these metadata fields are stored in archive item metadata and restored during extraction unless disabled.

Dependencies and integration points: create/extract metadata readers and writers, platform-specific ACL/xattr/flag APIs, `--numeric-ids`, `--noacls`, `--noxattrs`, `--noflags`, and `--read-special`.

Risks: platform and filesystem support differ substantially. Cross-platform restores can lose or map metadata imperfectly; Linux supports only selected flags; Cygwin ACL mapping is limited.

Test signals: platform matrix tests for ACL/xattr/flags, hardlink restoration, special-file metadata versus contents, timestamp precision, and metadata-disable options.
