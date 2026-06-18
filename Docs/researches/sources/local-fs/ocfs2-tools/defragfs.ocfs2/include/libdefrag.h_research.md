# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/libdefrag.h

## Role

`libdefrag.h` declares small support functions and print macros for `defragfs.ocfs2`.

## API

It declares `do_malloc()`, `do_read()`, `do_write()`, and `do_csum()`.

## Macros

It defines standardized error/status print macros for generic errors, file messages, errno-backed file errors, and message-plus-errno reports.

## Notes

The include guard misspells “defrag” as `__LIB_DEFERAG_H__`, but it is internally consistent.
