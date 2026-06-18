# sources/user-network-fs/samba/source3/smbd/smb2_trans2.c

## Purpose
This file implements most of Samba smbd's SMB1 trans2/NT transact file information behavior that is also reused by SMB2 query/set info paths. It is a translation layer between SMB wire information levels and Samba's internal file, directory, filesystem, EA, quota, stream, POSIX, rename, hardlink, allocation, timestamp, and delete-on-close operations.

The code is broad but organized around three jobs: marshal query replies, parse set-info requests, and enforce Windows/SMB semantics over Unix/VFS primitives. It handles legacy SMB1 levels, pass-through SMB2 levels, CIFS UNIX extensions, and SMB3 POSIX extension data.

## Important APIs, Types, And Functions
Key helper APIs include `refuse_symlink_fsp()`, `check_any_access_fsp()`, and `smb_roundup()`. `refuse_symlink_fsp()` blocks EA access on symlinks and pathrefs without a pathref fd. `check_any_access_fsp()` validates that at least one requested access bit was granted, with special snapshot/TWRP handling that maps non-read access to `NT_STATUS_MEDIA_WRITE_PROTECTED`. `smb_roundup()` applies the configured allocation roundup size only for Windows-like clients, not Samba or Linux CIFS clients.

The EA subsystem is centered on `get_ea_value_fsp()`, `get_ea_names_from_fsp()`, `get_ea_list_from_fsp()`, `fill_ea_buffer()`, `fill_ea_chained_buffer()`, `estimate_ea_size()`, `set_ea()`, and `read_ea_list()`. It maps Windows EA names into POSIX `user.*` xattrs, filters Samba-private xattrs such as DOS attributes, NT ACLs, reparse attributes, AppleDouble metadata, and DOS stream xattrs, and rejects invalid Windows EA names unless POSIX path semantics are in use.

Directory enumeration uses `smbd_dirptr_lanman2_entry()` and the internal `smbd_marshall_dir_entry()`. These support many info levels: old LanMan formats, SMB find directory/full/both/name/id formats, CIFS UNIX formats, and `FSCC_FILE_POSIX_INFORMATION`. The marshaller computes file size, allocation size, timestamps, mode bits, file ids, EA sizes or reparse tags, 8.3 short names, AAPL readdir attributes, padding, next-entry offsets, and resume-key slots.

Filesystem information is handled by `smbd_do_qfsinfo()` and `smbd_do_setfsinfo()`. Query levels include allocation, volume, attributes, label, size, full size, device, quota, object id, sector size, CIFS UNIX capability, POSIX filesystem info, and POSIX whoami. Setfsinfo only supports quota updates through `smb_set_fsquota()`.

File/path query information is handled by `smbd_do_qfilepathinfo()`. It emits standard/basic/EA/name/all/internal/access/position/mode/alignment/stream/compression/network-open/attribute-tag/POSIX information. Helper functions include `store_file_unix_basic()`, `store_file_unix_basic_info2()`, `map_info2_flags_from_sbuf()`, `map_info2_flags_to_sbuf()`, and `marshall_stream_info()`.

File/path mutation is handled by `smbd_do_setfilepathinfo()`. Important callees are `smb_set_info_standard()`, `smb_set_file_basic_info()`, `smb_set_file_time()`, `smb_set_file_dosmode()`, `smb_set_file_size()`, `smb_set_file_allocation_info()`, `smb_set_file_end_of_file_info()`, `smb_info_set_ea()`, `smb_set_file_full_ea_info()`, `smb_check_file_disposition_info()`, `smb_set_file_disposition_info()`, `smb_file_position_information()`, `smb_file_mode_information()`, `smb2_parse_file_rename_information()`, `smb_file_rename_information()`, `smb2_file_rename_information()`, `smb_file_link_information()`, and `hardlink_internals()`.

## Control Flow
Query control flow is mostly dispatch-by-information-level. Callers allocate or pass a response buffer; `smbd_do_qfsinfo()` and `smbd_do_qfilepathinfo()` grow the buffer with an additional safety margin, zero it, choose a case by info level, write little-endian fields with Samba macros, return `fixed_portion` for SMB2 framing where needed, and report the final data length.

Directory enumeration flows through a directory pointer. `smbd_dirptr_lanman2_entry()` derives the wildcard mask, applies long-name/8.3 matching in `smbd_dirptr_lanman2_match_fn()`, gets one matching entry through `smbd_dirptr_get_entry()`, marshals it, and pushes it back to the overflow queue if the entry does not fit. The marshaller calculates alignment before the record and record padding after the variable name payload, then writes the previous record's next offset through `last_entry_off`.

EA query flow lists xattrs with `SMB_VFS_FLISTXATTR()`, filters names, reads values with `SMB_VFS_FGETXATTR()`, drops zero-length or oversized values, converts names to DOS/ASCII form, and serializes either old SMB EA buffers or chained `FILE_FULL_EA_INFORMATION` buffers. EA set flow parses incoming EA records, validates access and names before applying any change, canonicalizes case against existing EAs, and uses `SMB_VFS_FSETXATTR()` or `SMB_VFS_FREMOVEXATTR()`.

Set-info control flow is similarly case-based. It validates minimal payload sizes, checks access rights close to each mutating operation, and then delegates to Samba VFS or common smbd helpers. Rename and link flows parse SMB1 or SMB2 wire name formats, convert paths relative to cwd or parent pathrefs, reject unsupported stream cases, then call `rename_internals_fsp()`, `rename_internals()`, or `SMB_VFS_LINKAT()`.

## State And Persistence Behavior
Most state is stored in existing smbd structures rather than in this file. It reads and updates `files_struct`, `smb_filename`, `connection_struct`, `smb_request`, file handle position, share-mode/delete-on-close state, DOS attributes, xattrs, timestamps, allocation size, file length, quotas, and notify state.

Persistent filesystem state changes include xattrs, quota settings, DOS mode storage, file timestamps, allocation and EOF length, hardlinks, renames, delete-on-close flags that apply across opens on the same dev/inode, and VFS-backed stream information. The file also emits change notifications through `notify_fname()` and triggers lease/dirlease break behavior for timestamp and hardlink changes.

Time handling is stateful. `smb_set_file_time()` rounds timestamps to the connection timestamp resolution, omits fields marked "no change", sets sticky write time on open files when requested, and calls `file_ntimes()`. File size and allocation updates call `prepare_file_modified()`, `mark_file_modified()`, `trigger_write_time_update_immediate()`, or `vfs_allocate_file_space()` to preserve Windows-visible update semantics.

## Dependencies And Integration Points
The file integrates heavily with Samba's VFS layer: xattrs, directory attributes, statvfs, file ids, allocation size, stream info, quota, linkat, create/open, chmod-like DOS mode, truncate, and timestamp operations all cross the VFS boundary. It also depends on Samba path conversion and name mangling code, SMB string conversion helpers, NDR encoders for SMB3 POSIX information, security tokens, access-check helpers, share-mode/delete-on-close logic, notify/lease code, reparse point helpers, and loadparm configuration.

SMB1 and SMB2 integration is intentional. Several public functions are called from both SMB1 trans2/NT transact handlers and SMB2 query/set info handlers, with protocol-specific branches such as `conn_using_smb2()`, `fsp->fsp_flags.posix_open`, SMB2 normalized names, SMB2 full EA chained buffers, and SMB2 rename wire parsing.

## Risks And Edge Cases
The largest risk is wire-format compatibility. Many cases have fixed offsets, padding, null-termination quirks, and client-specific comments. Small layout mistakes can break old clients, SMB2 `fixed_portion` calculation, directory enumeration continuation, or EA parsing.

Security-sensitive areas include symlink refusal for EA operations, protection of Samba-private xattrs, access checks for write attributes/data/EA, snapshot write protection, quota root checks, delete-on-close authorization, and hardlink/rename path conversion. Bugs here can expose metadata, permit mutation without rights, or allow unsafe path handling.

State correctness risks include sticky write times after writes, delete-on-close across multiple handles, allocation-size rounding that differs by client type, fallback opens for path-based size/allocation changes, and correct cleanup after temporary open failures. The hardlink path rejects directories, streams, existing targets without overwrite, and timewarp source paths, all of which should remain covered.

## Test Signals
Relevant tests are Samba smbtorture RAW-SFILEINFO, RAW-QFILEINFO, SMB2-QUERY-INFO, SMB2-SETINFO, SMB2-CREATE replay/rename variants, stream tests, EA tests, UNIX/POSIX extension tests, quota tests when enabled, and durable handle regression tests around delete-on-close and lease breaks. Manual probes should cover Windows clients, Linux CIFS clients, SMB1 UNIX extensions, SMB3 POSIX opens, AAPL directory attributes, reparse points, named streams, symlinks, snapshots, pathrefs, max-sized EA buffers, and insufficient response-buffer cases.
