# sources/sync-backup/casync/src/cadecoder.c

## Purpose

`cadecoder.c` implements `CaDecoder`, the low-level reader/restorer for casync archive streams. It consumes serialized `CaFormat*` objects from `caformat.h`, validates them against feature flags and format ordering rules, exposes stream events to callers, optionally writes decoded filesystem objects under a configured base fd, supports archive and path seeking, and maintains optional digests for the full archive, current payload, and hardlink identity.

The file is the inverse of the encoder side and is driven by the high-level API in `casync.c`. Callers repeatedly invoke `ca_decoder_step()`, respond to request events by feeding bytes with `ca_decoder_put_data()` or `ca_decoder_put_eof()`, respond to seek/skip events with the requested input movement, and inspect current object metadata or payload data through the public accessors declared in `cadecoder.h`.

## Important APIs, Types, and Functions

The private `CaDecoder` object stores the replay state: current `CaDecoderState`, archive feature flags, replay mask, a fixed-depth `nodes[NODES_MAX]` path stack, a `ReallocBuffer` of unread input, optional `CaOrigin` tracking for reflinks, archive/payload offsets, seek target fields, delete/reflink/hardlink/payload booleans, UID shift/range configuration, digest objects, and counters for punch-hole, reflink, and hardlink bytes.

Each `CaDecoderNode` represents one path-stack entry. It caches the parsed entry object, name, temporary name, offsets for entry/payload/goodbye/end, mode and size for naked objects, user/group strings, symlink target, device number, SELinux label, xattrs, ACL lists, file capabilities, quota project ID, optional payload origin, directory child names used for deletion reconciliation, and realization flags such as `hardlinked`.

The central public functions are:

- Construction and configuration: `ca_decoder_new()`, `ca_decoder_unref()`, `ca_decoder_set_base_fd()`, `ca_decoder_set_boundary_fd()`, `ca_decoder_set_base_mode()`, `ca_decoder_set_archive_size()`, `ca_decoder_set_feature_flags_mask()`, `ca_decoder_set_expected_feature_flags()`, and boolean setters for punch holes, reflinks, hardlinks, deletion, payload delivery, and immutable-bit undo.
- Event loop: `ca_decoder_step()`, `ca_decoder_put_data()`, `ca_decoder_put_eof()`, `ca_decoder_get_request_offset()`, `ca_decoder_get_seek_offset()`, `ca_decoder_get_skip_size()`, and `ca_decoder_get_payload()`.
- Metadata accessors: `ca_decoder_current_path()`, mode/target/mtime/size/uid/gid/user/group/rdev/offset/chattr/FAT/xattr/quota helpers, and `ca_decoder_current_archive_offset()`.
- Seeking: `ca_decoder_seek_offset()`, `ca_decoder_seek_path()`, `ca_decoder_seek_path_offset()`, and `ca_decoder_seek_next_sibling()`.
- Digest and dedupe support: archive/payload/hardlink digest enable/get functions plus `ca_decoder_try_hardlink()`.

Key private functions include the validation helpers for every serialized object type, `ca_decoder_parse_entry()`, `ca_decoder_parse_filename()`, `ca_decoder_parse_goodbye_tail()`, `ca_decoder_do_seek()`, `ca_decoder_step_node()`, `ca_decoder_advance_buffer()`, `ca_decoder_realize_child()`, `ca_decoder_finalize_child()`, `ca_decoder_node_reflink()`, `ca_decoder_node_delete()`, ACL conversion helpers, UID/GID name resolution helpers, and `ca_decoder_install_file()`.

## Control Flow

The decoder starts in `CA_DECODER_INIT`. Once a base fd, boundary fd, or base mode is configured, the root node exists and `ca_decoder_step()` advances any previously consumed buffer with `ca_decoder_advance_buffer()`, then dispatches to `ca_decoder_step_node()`.

For directory-tree archives, `CA_DECODER_ENTERED` and `CA_DECODER_ENTERED_FOR_SEEK` parse an entry sequence with `ca_decoder_parse_entry()`. That parser accepts a strict order: one `ENTRY`, optional user/group names, sorted xattrs, ordered ACL records, SELinux/fcaps/quota metadata, and then one type-specific terminator such as `PAYLOAD`, `FILENAME`, `GOODBYE`, `SYMLINK`, or `DEVICE`. It returns `CA_DECODER_REQUEST` until complete objects are buffered, returns negative errors for malformed streams, and returns `CA_DECODER_NEXT_FILE` when a new file entry is available.

After `CA_DECODER_ENTRY`, the decoder realizes a child under the parent if filesystem output is enabled. Directories enter `CA_DECODER_IN_DIRECTORY`; regular files enter `CA_DECODER_IN_PAYLOAD`; symlinks, fifos, devices, and sockets move toward `CA_DECODER_FINALIZE`.

Payload handling computes a bounded `step_size`, updates enabled digests, returns `CA_DECODER_PAYLOAD` when bytes are available, writes data to the target fd during the following `ca_decoder_advance_buffer()` call, and increments payload/archive offsets. If payload delivery and local writing are not needed, the decoder can emit `CA_DECODER_SKIP` for known-size payloads. EOF is accepted only for root naked payloads of unknown size; otherwise premature EOF is an error.

Directory handling alternates between `FILENAME` records and child entries until a `GOODBYE` object is parsed. Child names are accumulated for optional deletion reconciliation unless seeking invalidated the directory listing. On `GOODBYE`, the node caches the goodbye table and later finalizes the directory.

Finalization walks back up the node stack. `ca_decoder_finalize_child()` performs reflink attempts, deletion of absent directory entries, ownership and permission replay, ACLs, xattrs, file capabilities, SELinux labels, timestamps, atomic installation from temporary names, chattr/FAT attribute replay, subvolume checks, and post-restore timestamp granularity verification. Once root finalization completes, the state becomes `CA_DECODER_EOF` and `CA_DECODER_FINISHED` is returned.

Seeking is a separate group of states. Naked-file offset seeking uses `CA_DECODER_PREPARING_SEEK_TO_OFFSET` and `CA_DECODER_SEEKING_TO_OFFSET`. Path seeking uses cached node offsets, loaded `GOODBYE` tables, known goodbye offsets, or archive end offsets to jump to filename, entry, payload, goodbye, or goodbye-tail positions. `format_goodbye_search()` uses SipHash over path components and handles hash collisions with `seek_idx`. On successful seek, digest state may be reset or invalidated, and a boundary node prevents iteration above the selected subtree.

## State and Persistence Behavior

Decoder state is in-memory and mutable. It owns buffered input, parsed object copies, path stack nodes, open file descriptors, cached NSS lookups, cached filesystem type information, optional digest contexts, and optional origin metadata. `ca_decoder_unref()` frees node allocations, closes owned fds at index 3 or above, releases origins, digest contexts, cached strings, and buffer storage.

Filesystem persistence is optional. With a base fd or boundary fd, the decoder creates directories, files, symlinks, fifos, devices, sockets, Btrfs subvolumes, attributes, xattrs, ACLs, labels, quota project IDs, timestamps, and deletion side effects under the target tree. Regular files are written through temporary names and installed with `renameat()`, `renameat2(RENAME_EXCHANGE)`, or remove-and-rename fallback. Directory deletion removes entries not present in the archive when deletion is enabled and directory names were collected without invalidation.

Digest state is persistent across steps but tied to stream position. Archive digests are available only at EOF. Payload and hardlink digests are available only while a current node is in finalization, and seeking into the middle of payloads marks them stale. `ca_digest_read()` finalizes the underlying OpenSSL context, so digest getters are terminal reads for the current digest context.

UID/GID shifting is applied when replaying numeric owners and ACL qualifiers. User/group names are resolved through `getpwnam_r()` and `getgrnam_r()` with a one-entry cache. Root names are specially synthesized by current accessors when user-name feature flags are active but root was suppressed in the archive.

## Dependencies and Integration Points

Internal dependencies include `cadecoder.h`, `caformat.h`, `caformat-util.h`, `cautil.h`, `chattr.h`, `quota-projid.h`, `realloc-buffer.h`, `reflink.h`, `rm-rf.h`, `siphash24.h`, `time-util.h`, and generic `util.h` helpers. It relies on `CaOrigin`/`CaLocation` for reflink provenance and on `cadigest.c` through `CaDigest`.

System dependencies include Linux file APIs, POSIX ACLs, xattrs, `statfs`, `renameat2`, Btrfs ioctls, Linux chattr/FAT attribute headers, optional SELinux APIs, NSS user/group lookup, and block/device helpers. Several replay paths are Linux-specific and intentionally return `-EOPNOTSUPP`, `-EEXIST`, or related errno values when the backing filesystem cannot represent archived metadata.

The main integration caller is `casync.c`, which configures decoder knobs, feeds local or remote archive bytes, satisfies request/seek/skip events, reads payloads for API clients, asks for hardlink digests, and invokes `ca_decoder_try_hardlink()` against seed roots. The decoder also shares digest semantics with `caencoder.c`, `cachunkid.c`, cache/store/remote code, and feature-flag digest selection from `caformat-util`.

## Risks and Edge Cases

The parser is intentionally strict. Small deviations in object order, duplicate metadata, feature-flag mismatch, invalid UID/GID ranges, unsorted xattrs or ACLs, invalid goodbye tail offsets, malformed names, unexpected object types, or impossible metadata/type combinations all fail with `-EBADMSG` or related errors. This is good for integrity but makes compatibility with future or alternate encoders sensitive.

Filesystem replay has a broad side-effect surface. Risks include replacing the wrong file when caller-provided fds or boundaries are wrong, non-atomic fallback when `RENAME_EXCHANGE` is unavailable, partial temporary files after errors, deletion of destination entries absent from the archive, privileged metadata operations failing after data writes, NSS lookup differences across hosts, filesystem timestamp granularity mismatches, SELinux/xattr/ACL capability differences, Btrfs-specific behavior, and immutable-bit handling requiring explicit enablement.

Seeking depends on known archive sizes, correct node end offsets, and valid goodbye tables. It returns `-ESPIPE` when insufficient offset information exists and marks payload/hardlink digests stale for mid-stream seeks. Hash collisions are handled by retrying `seek_idx`, but malformed goodbye offsets can still abort with integrity errors.

Digest and dedupe behavior has subtle ordering constraints. Payload and hardlink digests are reset at entry boundaries and are valid only for complete sequential reads. Hardlink optimization performs superficial metadata checks before linking; it can silently decline on cross-device, unsupported, changed, or incompatible files.

## Test Signals

High-value tests should drive `ca_decoder_step()` through complete archives and assert the expected sequence of `REQUEST`, `NEXT_FILE`, `PAYLOAD`, `DONE_FILE`, and `FINISHED` events for regular files, naked files, directories, symlinks, devices, and metadata-rich entries.

Parser tests should cover truncated headers, invalid sizes, repeated entries, unsupported feature flags, feature-flag mismatches, invalid names, bad UID/GID encodings, unordered xattrs/ACLs, missing required ACL masks, default ACLs on non-directories, invalid symlink targets, malformed device majors/minors, and broken goodbye tail offsets.

Replay tests should run on filesystems with and without xattr/ACL/SELinux/Btrfs/FAT support, verifying graceful unsupported errors, correct temporary-file installation, deletion behavior, immutable-bit undo, hole-punch counters, reflink counters, hardlink counters, UID/GID shifting, and timestamp granularity checks.

Seek tests should set archive size and exercise naked offset seeks, path seeks, path-plus-payload-offset seeks, next-sibling seeks, not-found paths, hash-collision retry behavior, stale digest results after mid-payload seeks, and boundary behavior after a successful path seek.

Integration tests through `casync.c` should confirm that remote/local archive feeding satisfies decoder request offsets, skip/seek events are honored exactly, archive/payload/hardlink digests match encoder output, and restore/extract operations preserve expected tree metadata.
