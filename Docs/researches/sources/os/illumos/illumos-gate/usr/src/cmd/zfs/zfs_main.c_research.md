# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_main.c

This is the main implementation of the illumos `zfs` userland command. It owns the command table, command-line parsing, high-level user workflows, output formatting, mount helper behavior, and calls into libzfs/libzfs_core for the actual ZFS operations.

Global state and setup:
- Defines global `libzfs_handle_t *g_zfs`, shared with helper files through `zfs_util.h`.
- Maintains `mnttab_file`, command history text, and `log_history`.
- Initializes locale, text domain, libzfs, mount table access, error printing, and libzfs mount-table caching in `main()`.
- Saves command arguments for pool history logging and logs successful commands unless a subcommand already logged history itself.
- Supports `ZFS_ABORT` to abort on exit for leak/debug workflows.
- In DEBUG builds, configures libumem debug/logging defaults.

Command dispatch:
- `command_table` maps command names to implementations and usage IDs.
- Supported commands include dataset lifecycle (`create`, `destroy`, `snapshot`, `rollback`, `clone`, `promote`, `rename`, `bookmark`, `remap`), reporting/property commands (`list`, `get`, `set`, `inherit`, `upgrade`, `userspace`, `groupspace`, `projectspace`, `project`), data transfer (`send`, `receive`), sharing/mounting, delegation (`allow`, `unallow`), holds, encryption key commands, and channel programs.
- Aliases are handled in `main()`: `umount` maps to `unmount`, `recv` maps to `receive`, and `snap` maps to `snapshot`.
- If the command token contains `=`, `main()` treats the invocation as implicit `zfs set`.
- If invoked as filesystem helper program `mount` or `umount`, it routes to `manual_mount()` or `manual_unmount()` instead of normal subcommand parsing.

Common helpers:
- `usage()` prints full or command-specific usage and property/delegation help hints.
- `parseprop()` parses and de-duplicates `property=value` arguments into nvlists, modifying the input string in place.
- `parsepropname()` parses receive `-x` property exclusions.
- `parse_depth()` validates recursive depth options and enables recursive iteration flags.
- `safe_malloc()`, `safe_realloc()`, and `safe_strdup()` exit through `nomem()` on allocation failure.
- Progress helpers implement delayed terminal progress for long operations such as mount-all.
- `zfs_mount_and_share()` mounts and shares newly created filesystems when `canmount=on`.

Dataset creation and clone commands:
- `zfs_do_create()` creates filesystems or volumes, parses `-o`, `-V`, `-b`, `-s`, `-p`, dry-run, verbose, and parseable modes.
- Volume creation rounds `volsize` up to `volblocksize` and sets `reservation` or `refreservation` unless `-s` disables reservation.
- Dry-run validates properties against the target pool without creating the dataset.
- Parent creation uses `zfs_create_ancestors()` for `-p`.
- `zfs_do_clone()` opens a snapshot, optionally creates missing ancestors, calls `zfs_clone()`, then mounts/shares the clone.

Destroy, rollback, and snapshot commands:
- `zfs_do_destroy()` handles filesystem/volume destruction, snapshot ranges, bookmarks, recursive destruction, dependent clone checks, dry-run output, deferred snapshot destruction, and batched snapshot deletion through nvlists.
- Snapshot destruction supports snap specs and recursive filesystem traversal, calculates reclaimable space for verbose output, and can destroy dependent clones for `-R`.
- Bookmark destruction validates bookmark existence and uses `lzc_destroy_bookmarks()`.
- `zfs_do_rollback()` opens the target snapshot and parent dataset, checks for newer snapshots/bookmarks and clone dependents, and then calls `zfs_rollback()`.
- `zfs_do_snapshot()` builds an nvlist of snapshots, supports recursive snapshots, skips inconsistent descendants during recursive traversal, and creates all requested snapshots with one `zfs_snapshot_nvl()` call.

Property and listing commands:
- `zfs_do_get()` parses columns, sources, types, recursion/depth, scripted output, and literal output. It prints native properties, user properties, user/group/project quota pseudo-properties, written properties, and received values when requested.
- `zfs_do_set()` accepts one or more `property=value` arguments followed by one or more datasets, validates argument ordering, and calls `zfs_prop_set_list()` for each dataset.
- `zfs_do_inherit()` validates readonly/non-inheritable properties, supports `-S` received-value reversion, and optionally recurses while skipping invalid property/type combinations.
- `zfs_do_list()` parses output fields, types, sort keys, recursion/depth, scripted and literal output. It relies on `zfs_for_each()` for ordering and property expansion and prints aligned table output.
- `zfs_do_upgrade()` lists filesystem versions, reports older/newer datasets, or upgrades filesystem `version` properties after checking required pool SPA versions.

Userspace, groupspace, and projectspace reporting:
- `zfs_do_userspace()` implements the shared backend for `userspace`, `groupspace`, and `projectspace`.
- It gathers user/group/project used/quota and object used/quota records with `zfs_userspace()`.
- It can translate SMB SIDs to POSIX IDs, print numeric names, select output fields, filter entity types, and sort by requested fields.
- It stores rows in libuutil AVL/list structures, calculates output widths, and prints either aligned or scripted output.

Send and receive:
- `zfs_do_send()` supports incremental sends, replication, properties, parsable/verbose/dry-run output, large blocks, embedded data, compressed/raw streams, holds, backup mode, and resume-token sends.
- It refuses to write binary streams to a terminal unless dry-run mode is active.
- It has a special path for sending a filesystem or sending from a bookmark through `zfs_send_one()`, and otherwise uses `zfs_send()`.
- Extra verbose mode can dump send debug nvlists to stderr after redirecting stdout back to stderr.
- `zfs_do_receive()` parses property overrides/exclusions, prefix/tail target modes, holds skipping, dry-run, no-mount, resumable receives, force rollback, verbose mode, and abort-resumable mode.
- It refuses to read a stream from a terminal and calls `zfs_receive()` for normal receives.
- Abort-resumable mode destroys either the `%recv` temporary dataset or an inconsistent dataset with a receive resume token.

Delegated permissions:
- Defines the user-visible delegated permission names and maps them to `zfs_deleg_note_t` notes.
- `allow_usage()` prints allowed permissions and writable properties.
- The parser validates combinations of `-l`, `-d`, `-u`, `-g`, `-e`, `-c`, `-s`, and recursive unallow.
- `construct_fsacl_list()` builds encoded fsacl nvlists for users, groups, everyone, create-time permissions, and named permission sets.
- Permission display parses existing fsacl nvlists into filesystem, subject, and permission AVL/list structures, resolves user/group names where possible, and prints local, descendant, and local+descendant permissions.
- `zfs_do_allow()` and `zfs_do_unallow()` share `zfs_do_allow_unallow_impl()`, using `zfs_get_fsacl()` and `zfs_set_fsacl()`; recursive unallow walks child filesystems.

Holds:
- `zfs_do_hold()` and `zfs_do_release()` share hold/release parsing and call `zfs_hold()` or `zfs_release()` for each snapshot.
- Hold tags beginning with `.` are rejected as reserved for libzfs.
- `zfs_do_holds()` collects hold nvlists, supports recursive matching by snapshot short name, and prints name/tag/timestamp rows in aligned or scripted form.

Mount/share and unmount/unshare:
- `share_mount()` implements `zfs mount` and `zfs share`.
- `share_mount_one()` enforces zone restrictions, `mountpoint`, `sharenfs`, `sharesmb`, `canmount`, encryption key availability, and resumable receive consistency before mounting or sharing.
- Mount-all gathers all filesystems, sorts them by mountpoint through libzfs helpers, and can run mount operations in parallel; share-all avoids parallel libshare usage because libshare is not MT-safe.
- `zfs mount` with no arguments lists mounted ZFS filesystems from `/etc/mnttab`.
- `unshare_unmount()` implements `zfs unmount` and `zfs unshare`, including `-a` traversal through `/etc/mnttab`, reverse mountpoint ordering for unmount-all, legacy mount/share handling, and path-based unmount/unshare resolution.
- `manual_mount()` supports `/etc/fs/zfs/mount` only for datasets whose `mountpoint` is `legacy`; otherwise it tells the user to use ZFS properties.
- `manual_unmount()` accepts path-based unmounts and delegates to the shared path resolver.

Other commands:
- `zfs_do_rename()` supports normal renames, recursive snapshot renames, parent creation, and forced unmount during rename.
- `zfs_do_promote()` promotes clone filesystems/volumes.
- `zfs_do_diff()` validates snapshots, opens the dataset, ignores `SIGPIPE`, and calls `zfs_show_diffs()`.
- `zfs_do_remap()` calls `zfs_remap_indirects()` for a filesystem or volume.
- `zfs_do_bookmark()` validates bookmark syntax, supports relative `@snap` source names, and calls `lzc_bookmark()`.
- `zfs_do_channel_program()` reads a Lua channel program from a file or stdin, applies instruction/memory limits, passes remaining CLI arguments as an nvlist string array, executes sync or nosync channel programs, and prints JSON or nvlist-style output.
- `zfs_do_load_key()` and `zfs_do_unload_key()` share recursive/all-dataset key load/unload logic, counting attempted and failed encryption roots.
- `zfs_do_change_key()` optionally loads the current key, parses encryption properties, and calls `zfs_crypto_rewrap()`.
- `zfs_do_project()` parses project quota file-tree operations and delegates file handling to `zfs_project_handle()`.

Risk notes:
- This file is the administrative command surface for destructive operations; option validation, dry-run behavior, and dependent traversal are safety-critical.
- Several parsers intentionally mutate `argv` strings in place by inserting NUL delimiters; later code must not assume original argument text remains intact.
- Destroy and rollback depend on snapshot/bookmark ordering and clone detection to avoid unsafe partial deletion.
- Mount/share behavior depends on live `/etc/mnttab`, zone state, encryption key state, libshare initialization, and receive-resume state.
- Delegation encoding uses compact string keys in nvlists; mistakes in type/locality/name encoding can grant or revoke the wrong permissions.
- Userspace/projectspace output combines identity translation, sorting, and quota properties; changes can affect both human and scripted output.
- Send/receive paths intentionally guard terminal stdin/stdout because the streams are binary.
- History logging is suppressed manually by a few commands after they log per-pool history themselves; adding cross-pool mutations must account for this.
