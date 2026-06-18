<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.c -->
# sources/user-network-fs/samba/source3/locking/leases_db.c

## Purpose
`leases_db.c` maintains `leases.tdb`, the reverse mapping from SMB2 lease identity to the files currently attached to that lease. It stores lease state, break state, version/epoch, and the per-file names needed to update lease metadata across rename and close paths.

## Important APIs, Types, And Functions
The public API is `leases_db_init`, `leases_db_add`, `leases_db_del`, `leases_db_parse`, `leases_db_rename`, `leases_db_set`, `leases_db_get`, `leases_db_get_current_state`, and `leases_db_copy_file_ids`. Internally, `leases_db_key` serializes `struct leases_db_key` from client GUID plus SMB2 lease key into a fixed 32-byte key. `leases_db_do_locked` centralizes locked record update: decode `struct leases_db_value`, call a mutator, delete empty records, or NDR-store updated values.

## Control Flow
Mutating callers enter `leases_db_do_locked`, which lazily opens the database read/write, locks the key, decodes any existing NDR value, and invokes an operation-specific callback. Add rejects duplicate file ids, initializes lease-wide state on the first file, appends a `leases_db_file`, and stores. Delete swaps the target file with the last entry and may cause whole-record deletion. Rename finds the matching file id and rewrites service path, base name, and stream name. Set updates lease-wide current/break state and epoch only when the record already has files. Read paths use `dbwrap_parse_record` with NDR decode, except `leases_db_get_current_state`, which peeks the first NDR uint32 for speed and uses the database sequence number to skip unchanged reads.

## State And Persistence
`leases.tdb` is a volatile sequence-numbered TDB opened at lock order 4. Keys are fixed NDR encodings of `(client_guid, lease_key)`. Values are NDR-encoded `struct leases_db_value` records containing current state, breaking fields, lease version, epoch, and a counted `files` array. `leases_db_get_current_state` relies on `current_state` staying the first encoded field, which is explicitly documented in the source.

## Dependencies And Integration Points
The file depends on dbwrap, TDB, Samba NDR generated code for `leases_db`, `file_id` comparison, and SMB2 lease structures. It is called from share-mode logic for adding/removing stale leases, from rename handling to update path metadata, and from `leases_util.c`/strict-locking checks to read current lease state cheaply.

## Risks And Test Signals
The fast current-state reader is fragile if the generated NDR layout changes. Add/delete use swap-with-last semantics, so callers must not depend on file order. Several callbacks carry string pointers into the decoded value and rely on immediate NDR push before caller-owned strings disappear. Empty-record deletion makes missed `modified` flags visible as stale leases. Useful tests include duplicate add rejection, delete of last file deleting the record, rename propagation, malformed NDR records, sequence-number cache behavior, break-state updates, and lease records with multiple stream/base-name combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.c -->
