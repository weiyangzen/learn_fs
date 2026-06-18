# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/debugfs.ocfs2.8.in

## Role

This is the manual page template for `debugfs.ocfs2`.

## Documented Interface

It documents interactive mode, command-file mode (`-f`), one-shot command mode (`-R`), backup superblock selection (`-s`), image mode (`-i`), read-write mode (`-w`), no-prompt mode, version/help, trace/log control (`-l`), and standalone lockname encode/decode modes.

## Filespec Semantics

The man page defines path resolution for inode numbers or locknames in angle brackets, absolute filesystem paths, paths relative to debugfs current directory, and `//` paths relative to the OCFS2 system directory.

## Command Documentation

The page lists and describes all supported debug commands: block mapping, file dump/cat, directory navigation/listing, metadata stats, journal dump, group/extent inspection, directory-index inspection, xattrs, refcount trees, heartbeat/slotmap/system-directory dumps, live OCFS2/DLM lock state, o2net stats, inode-to-path and block-to-inode searches, and recursive dumping.

## Notable Notes

It states that `gd_free_bits -s` requires `debugfs.ocfs2 -w`, and that live lock/net commands require debugfs mounted at `/sys/kernel/debug` unless reading saved files.
