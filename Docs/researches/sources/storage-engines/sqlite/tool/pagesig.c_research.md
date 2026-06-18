# sources/storage-engines/sqlite/tool/pagesig.c

## Purpose

Small diagnostic program that computes a signature for every page in one or more SQLite database files. It is intended to help analyze logs from `ext/misc/vfslog.c` by producing stable, compact page-content identifiers.

## Important APIs, control flow, and dependencies

`vlogSignature()` emits either a full hex dump for blocks of 16 bytes or less, or the first eight bytes plus a simple 64-bit additive checksum for larger blocks. `computeSigs()` opens a file, reads the database header, decodes the page size from bytes 16 and 17, validates it as a power of two, then reads and signs each full page. `main()` applies `computeSigs()` to each command-line file.

## State, persistence, and integration

The utility is read-only and depends only on stdio. It trusts the SQLite database header enough to determine page size and treats a header value of 1 as 65536 bytes. It does not parse b-trees or journals; the output is a page-number to signature list suitable for comparing page writes with VFS logs.

## Risks and test signals

The checksum is diagnostic, not cryptographic, and includes host-dependent behavior from casting page bytes to `unsigned int *`. Short files, invalid page sizes, and partial final pages are skipped with minimal diagnostics. Test signals include known database files, modified single pages producing changed signatures, invalid page-size handling, and comparison with vfslog page write traces.
