# sources/user-network-fs/samba/source3/librpc/idl/leases_db.idl

## Purpose
`leases_db.idl` defines the key and value records for Samba's SMB2 lease database. It is a persistence schema for tracking lease state per client GUID and lease key, plus the files attached to that lease.

## Important APIs, types, and functions
- `leases_db_key` combines `GUID client_guid` with `smb2_lease_key lease_key`.
- `leases_db_file` stores `file_id`, service path, base name, and stream name.
- `leases_db_value` stores current lease state, break-in-progress state, requested/required break targets, lease version, epoch, and an array of attached files.

## Control flow
The IDL has no executable flow, but it encodes the state transitions expected by SMB2 lease-break code. When `breaking` is true, `current_state > breaking_to_requested >= breaking_to_required` describes the in-progress downgrade sequence and possible multiple round trips.

## State and persistence behavior
This is durable or clustered database state. It preserves lease identity, file membership, state bits, epoch, and break progress so another process/node can reason about leases consistently. Strings are stored as UTF-8.

## Dependencies and integration points
The schema imports miscellaneous types, SMB2 lease structures, and file IDs. Generated NDR code is built into the `NDR_LEASES_DB` subsystem and used by lease database code for record serialization.

## Risks and edge cases
Lease break fields must remain internally ordered and consistent. Version/epoch handling affects client cache coherency. Multi-file arrays must match `num_files`, and path strings must be normalized consistently across nodes. Schema changes can break existing TDB/cluster records.

## Test signals
Exercise lease creation, multi-file lease updates, break request/ack sequences, epoch changes, serialization round trips, and recovery from stored records after process restart or clustered failover.
