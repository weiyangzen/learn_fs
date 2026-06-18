# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/atime_update_behavior.rs

Purpose: Defines the policy trait for deciding whether read access should update atime.

Important APIs/types/functions: `AtimeUpdateBehavior` has `should_update_atime_on_file_or_symlink_read` and `should_update_atime_on_directory_read`, both receiving previous atime, mtime, and current time.

Control flow: no implementation lives here. `DirEntryList::maybe_update_access_timestamp` dispatches to the appropriate method based on entry type.

State and persistence behavior: no state. Implementors influence whether a directory entry becomes dirty and later serialized.

Dependencies and integration points: used by `DirBlob::maybe_update_access_timestamp_of_entry` and policy implementations elsewhere in CryFS.

Risks: policy decisions affect write amplification and POSIX timestamp semantics. Implementors must handle clock skew or equal timestamps consistently.

Test signals: policy-specific tests should verify relatime/noatime/strict-atime behavior for file, symlink, and directory reads.
