# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/record.h

## Role

`record.h` defines the resume-record model for interrupted `defragfs.ocfs2` runs.

## Data Model

`struct resume_record` stores mode flags, the inode number where traversal should resume, argument count, and a list of target paths. `struct argv_node` stores one target path and list linkage.

The resume file is named `.ocfs2.defrag.record` under `/tmp`.

## API

It declares record dump, record-file path setup, record allocation/freeing, record fill/store/load/move/remove helpers, and argument-node freeing.

## Risk Areas

The record file stores raw struct header bytes plus variable strings and a checksum, so format portability depends on local ABI assumptions.
