# File Research: sources/os/plan9/9front/sys/src/cmd/replica/updatedb.c

Scans a root using a proto file and updates or logs a replica database. Emits change log records for adds, content changes, metadata changes, and deletes.

Options support changes-only mode, log-only mode, proto/root/time/uid overrides, excludes, and path filters. The database mark bit distinguishes visited entries from removals.

Warnings that look like network/I/O failures abort to avoid treating an unavailable tree as mass deletion.
