# File Research: sources/virtualization/libguestfs/daemon/ls.c

Implements directory listing APIs.

Important behavior:
- `do_ls0` streams NUL-terminated entry names through FileOut, excluding `.` and `..`.
- Once streaming begins, errors cancel the FileOut transfer.
- `do_ll` and `do_llz` resolve a chrooted realpath, convert it to sysroot path, then run `ls -la` or `ls -laZ`.

Filesystem relevance: directory enumeration and long-listing views of guest paths.
