# sources/user-network-fs/samba/source3/printing/rap_jobid.c

## Purpose

`rap_jobid.c` maintains an in-memory bidirectional mapping between Samba/spoolss 32-bit print job IDs and legacy RAP/LANMAN 16-bit job IDs. This supports downlevel APIs that cannot represent full spoolss job IDs.

## Important APIs, Types, and Functions

- `struct rap_jobid_key` combines `fstring sharename` and `uint32_t jobid` for the spoolss-side key.
- `pjobid_to_rap()` returns an existing RAP ID or allocates a new nonzero 16-bit ID and stores both forward and reverse records.
- `rap_to_pjobid()` resolves a RAP ID back to sharename and 32-bit job ID.
- `rap_jobid_delete()` removes both mapping directions for a given share/job ID.

## Control Flow

The first mapping request lazily creates an internal TDB with `TDB_INTERNAL`. `pjobid_to_rap()` looks up the compound key; if found, it returns the stored RAP ID. Otherwise it increments `next_rap_jobid`, skips zero, stores compound-key to RAP-ID and RAP-ID to compound-key records, and returns the new ID. Reverse lookup builds a 2-byte key and expects a `struct rap_jobid_key` value. Deletion first finds the RAP ID from the compound key, then deletes both records.

## State and Persistence

All mappings are process-local and in-memory only. They do not survive process exit. Keys are raw struct bytes for the compound key and two-byte little-endian values for RAP IDs.

## Dependencies and Integration Points

The file depends on TDB internal databases, Samba byte-order helpers, `fstring`, and debug utilities. It is used by `printspoolss.c` when creating or terminating spoolss jobs and by `printing.c` when print jobs are deleted.

## Risks and Edge Cases

- RAP IDs wrap at 16 bits; only zero is skipped, so old mappings can collide after enough allocations if not deleted.
- Raw struct keys depend on stable struct layout and zero-initialization.
- Mappings are per-process, so cross-process RAP lookup only works when the same process handles both operations.

## Test Signals

Tests should cover idempotent forward lookup, reverse lookup with sharename output, deletion of both directions, zero-skip behavior on wrap, and failure when lookup happens before any mapping exists.
