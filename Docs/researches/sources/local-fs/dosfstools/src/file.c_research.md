# File Research: sources/local-fs/dosfstools/src/file.c

Path descriptor and short-name utility code for fsck drop/undelete operations.

Main functions:
- `file_name()` formats an 11-byte DOS 8.3 name as printable text, using codepage conversion and octal escapes.
- `file_cvt()` converts user-entered pretty names to fixed 8.3 uppercase DOS form, accepting `\ooo` octal escapes.
- `file_add()` registers an absolute path for later drop or undelete action in an `FDSC` tree.
- `file_cd()` descends into the descriptor tree for subdirectory traversal.
- `file_type()` returns whether a current directory entry should be dropped or undeleted.
- `file_modify()` applies the registered operation to an in-memory directory entry name and consumes the descriptor.
- `file_unused()` reports registered drop/undelete requests that were never matched.

Data model:
- Global `fp_root` points to a tree of `FDSC` path descriptors.
- `FD_TYPE` differentiates no action, drop, and undelete.

Consumers:
- `fsck.fat.c` registers `-d PATH` and `-u PATH`.
- `check.c` calls `file_type`, `file_modify`, `file_cd`, and `file_unused`.

Research notes:
- The path matching is based on fixed 8.3 names, not long filenames.
- Undelete matching ignores the first byte when the on-disk entry has `DELETED_FLAG`.
