# sources/sync-backup/rsync/flist.c

## Purpose

`flist.c` builds, serializes, receives, sorts, searches, and frees rsync file lists. It is the bridge between source filesystem discovery and the transfer/generator pipeline. On the sender it walks argv or `--files-from` input, applies path cleanup and filters, creates compact `struct file_struct` entries, transmits them using rsync protocol flags, and emits additional incremental recursion file lists. On the receiver/generator side it decodes those wire entries, validates untrusted names, maps ids, reconstructs file metadata, sorts/deduplicates the list, and provides lookup helpers used by deletion, fuzzy matching, and hard-link handling.

## Important APIs, Types, And Functions

Key exported state includes `cur_flist`, `first_flist`, `dir_flist`, `send_dir_ndx`, `send_dir_depth`, `flist_cnt`, `file_total`, `file_old_total`, `flist_eof`, `io_error`, `filesystem_dev`, `flist_csum_len`, and `xfer_flags_as_varint`. These globals are consumed by the generator, receiver, hard-link code, id mapping, progress reporting, and incremental recursion scheduler.

Important entry points are `init_flist()`, `send_file_list()`, `recv_file_list()`, `send_extra_file_list()`, `recv_additional_file_list()`, `make_file()`, `unmake_file()`, `get_dirlist()`, `flist_find()`, `flist_find_name()`, `flist_find_ignore_dirness()`, `flist_free()`, `clear_file()`, `f_name_cmp()`, `f_name_has_prefix()`, `f_name_buf()`, `f_name()`, `link_stat()`, `change_pathname()`, and `get_device_size()`.

The central internal functions are `send_file_entry()` and `recv_file_entry()`, which implement the on-wire metadata format; `send_file_name()` and `send_directory()`, which discover files and append them to lists; `send_implied_dirs()` and `send1extra()`, which support `--relative` and incremental recursion; `flist_sort_and_clean()`, which sorts, strips roots, removes duplicates, and prunes empty dirs; and `flist_new()`, `flist_expand()`, and `flist_done_allocating()`, which manage list and pool allocation.

## Control Flow

`init_flist()` computes the file-list checksum length from the negotiated file checksum algorithm and enables file-list progress output when appropriate. The sender enters `send_file_list()`, initializes list objects and optional hard-link state, starts output buffering, then repeatedly reads source names from argv or `--files-from`. Each name is sanitized, split into directory and basename when needed, normalized for `--relative`, checked for unsafe `..`, daemon exclusions, server filters, directory transfer policy, and missing-arg behavior. Existing source args become `file_struct` entries via `send_file_name()`, and directories trigger `send_directory()` or incremental-recursion diversion.

`make_file()` is the local filesystem-to-`file_struct` constructor. It runs `readlink_stat()` or uses a supplied stat result, applies filters and `-x` mount rules, handles `--copy-devices`, records uid/gid, mtimes, optional atime/crtime, symlink text, device ids, hard-link dev/inode cache values, long file lengths, and optional checksums. The entry is allocated either from the current file-list pool or as a temporary standalone object.

`send_file_entry()` serializes a `file_struct`. It maintains static last-value caches for name, mode, uid, gid, mtime, atime, device major, and hard-link group data, then sets `XMIT_*` flags to avoid repeating unchanged fields. It writes compressed name-prefix data, length, times, mode, ids and optional id names, rdev, symlink target, old-protocol hard-link dev/inode values, and optional file checksums. `recv_file_entry()` reverses that format, including protocol-version branches, name iconv, path safety checks, sender-filter trust validation, hard-link reference expansion, device/special handling, ACL/xattr reception, and pool allocation.

After discovery, `send_file_list()` sends the end marker and sorts the list. In non-incremental mode it sends id lists and sets `flist_eof`. In incremental recursion it builds `dir_flist` tree links with `add_dirs_to_tree()` and can call `send_extra_file_list()` to send child directory batches. `send_extra_file_list()` walks the directory tree, sends `NDX_FLIST_OFFSET - dir_ndx` headers, emits a child file list with `send1extra()`, updates file totals and stats, then advances to child or sibling dirs until it writes `NDX_FLIST_EOF`.

The receiver calls `recv_file_list()` for the initial list and later incremental lists. It validates directory indices against `dir_flist`, reads xflags until an end marker, decodes each entry, enforces incremental path locality, updates file type counters, builds sorted pointers, receives id lists for old/non-incremental protocols, sorts and cleans, and merges received io-error flags. `recv_additional_file_list()` handles the special one-item initial list case by reading either EOF or an additional directory list.

Search and sort behavior is specialized for rsync semantics. `f_name_cmp()` compares virtual full paths without materializing strings and treats directories with path-like trailing slash ordering for protocol 29 and later. `flist_sort_and_clean()` uses stable merge sort by default, removes duplicate names on the receiver by clearing inactive entries, marks duplicate directories on the sender, strips leading roots for relative paths after sorting, and implements empty-directory pruning by temporarily overloading depth values.

## State And Persistence

The file-list lifecycle is in-memory and protocol-stream-backed. Non-temp file lists share an allocation pool and form a circular-prev/linear-next list. `file_total`, `file_old_total`, and `flist_cnt` track active work and incremental cleanup. Temp lists are used for directory scans such as deletion and fuzzy matching. `io_error` persists file-list construction errors across send/receive and is deliberately sent to the peer to protect delete modes. Static caches in `send_file_entry()` and `recv_file_entry()` are protocol state; they rely on sequential entry processing. `pathname`, `orig_dir`, and `pathname_len` cache sender cwd transitions.

## Dependencies And Integration Points

This file depends heavily on `rsync.h` macros and extra-field layout, `ifuncs.h` helpers, `inums.h` number formatting, `io.h` wire I/O, the memory-pool allocator, filter APIs, id-list APIs, ACL/xattr APIs, iconv conversion, hard-link helpers from `hlink.c`, filesystem wrappers such as `do_stat_at()` and `x_lstat()`, and generator-side consumers such as `delete_in_dir()` and `recv_generator()`. The generator relies on sorted `cur_flist`, `dir_flist`, `F_DEPTH`, `FLAG_CONTENT_DIR`, `FLAG_TOP_DIR`, hard-link group fields, and `flist_find*()` lookups.

## Risks

The highest-risk areas are protocol compatibility branches, name/path validation, static compression state, and extra-field sizing. A mismatch in `XMIT_*` flags or protocol version handling corrupts the wire stream. Unsafe path handling can become a traversal vulnerability, so checks around `clean_fname()`, absolute names, daemon filters, implied filters, and `sanitize_path()` are security-critical. `MAXPATHLEN` calculations protect stack buffers but need regression coverage. Duplicate handling and empty-dir pruning temporarily reuse fields, making ordering and active-entry assumptions fragile. Incremental recursion uses multiple shared globals and parent/child indices; off-by-one errors can strand lists or free pools too early. Long sizes, nanosecond mtimes, device ids, and hard-link group fields all depend on conditional extra allocation.

## Test Signals

Useful tests include recursive and non-recursive file-list builds; `--relative`, `/./`, trailing slash, `.` and `..` rejection cases; daemon and server filter rejection; `--files-from` with null and newline separators; iconv filename and symlink conversion; protocol compatibility for 28, 29, 30, and 31 features; `--delete-missing-args`; `--one-file-system`; duplicate file and directory names; `--prune-empty-dirs`; large files over 4 GiB; nanosecond mtimes; ACL/xattr preservation; device/special preservation; symlink munging and unsafe symlink copy behavior; incremental recursion with additional file lists; and hard-link transfers across initial and later file lists.
