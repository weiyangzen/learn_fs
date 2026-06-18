## sources/user-network-fs/samba/source3/lib/tdb_validate.h

Purpose: public interface for TDB validation and backup handling. It defines the validation status structure, callback type, and three validation entry points.

Important API/type details: `struct tdb_validation_status` is passed to validation callbacks through the generic private state pointer and lets callbacks mark bad entries or unknown keys while setting `success=false`. `tdb_validate_data_func` matches `tdb_traverse`-style callbacks. `tdb_validate` operates on an open TDB, `tdb_validate_open` opens by path, and `tdb_validate_and_backup` validates plus backup/restore side effects.

Control flow contract: callbacks should inspect each `TDB_DATA` key/value, update the provided status, and return traversal-compatible status. A zero return from validation APIs means good or restored; nonzero means validation/repair failed.

State and persistence: the header itself has no state. `tdb_validate_and_backup` is documented to write `.bak`, `.bak.old`, and `.corrupt` files as needed, so callers must pass paths where those sidecar files are acceptable.

Risks and tests: consumers must understand that backup creation failure after successful validation is not surfaced as failure by the implementation. Callback misuse can produce false success. Tests should include callback status flag behavior and path permissions for sidecar backup files.
