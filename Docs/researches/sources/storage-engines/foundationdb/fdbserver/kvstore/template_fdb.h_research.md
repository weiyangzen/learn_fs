# sources/storage-engines/foundationdb/fdbserver/kvstore/template_fdb.h

## Purpose
This header embeds two binary SQLite/FoundationDB template database images as C string literals. They are used to initialize kvstore database files with and without SQLite page checksums.

## Important APIs, Types, And Functions
The file declares `static const char template_fdb_without_page_checksums[]` and `static const char template_fdb_with_page_checksums[]`. There are no functions or types. The arrays begin with the FoundationDB-specific file signature bytes and contain fixed binary page data.

## Control Flow
There is no runtime control flow in this header. Consumers include one of the arrays and write its bytes into a new database file depending on whether page checksums are enabled.

## State And Persistence Behavior
The arrays are immutable process data compiled into the binary. When copied to disk they become the initial persistent state for a kvstore file. A one-byte change can alter database format, header flags, page checksums, or bootstrap metadata.

## Dependencies And Integration Points
The header has no includes and depends only on C/C++ string literal concatenation. It integrates with SQLite kvstore creation code and any tests validating page-checksum mode.

## Risks And Test Signals
Because this is opaque binary data, review is difficult and normal formatters must not rewrite it. Tests should create stores from both templates, open them with the expected checksum setting, verify integrity checks, and ensure array byte lengths/checksum bytes match the SQLite format expected by the kvstore implementation.
