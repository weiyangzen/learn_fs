# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_util.h

Tiny directory utility header.

Defines `is_dots(const char *name, unsigned int len)`, returning true for `.` and `..` only. It is used by directory iteration and scan code to implement exclude-dot flags and by indexed-directory hashing to special-case dot entries.
