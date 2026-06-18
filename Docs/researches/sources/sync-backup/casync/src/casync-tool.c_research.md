# sources/sync-backup/casync/src/casync-tool.c

## Purpose

`casync-tool.c` is the command-line frontend for the `casync` executable. It parses global options, selects a verb, validates locators and file types, configures the appropriate synchronization/remoting/device object, and drives long-running state machines until completion or signal-triggered shutdown. The file does not implement chunking, archive parsing, store persistence, compression, FUSE, NBD, or remote protocol framing itself; instead it is the integration layer over `CaSync`, `CaRemote`, `CaStore`, `CaIndex`, `CaBlockDevice`, FUSE, GC, notification, logging, signal, and formatting utilities.

The public verbs handled here are `make`, `extract`, `list`, `mtree`, `stat`, `digest`, `mount`, `mkdev`, and `gc`. It also exposes internal verbs: `pull` and `push` for SSH-style remoting, and `udev` for NBD udev rule integration.

## Important APIs, Types, And Functions

The global option state is held in static `arg_*` variables. Important knobs include `arg_what`, logging/verbosity/dry-run, chunk size bounds, digest and compression selection, feature flag inclusion/exclusion, store and extra store paths, seed paths, cache settings, extraction behaviors (`delete`, `reflink`, `hardlink`, `punch_holes`, `undo_immutable`, `seed_output`), listing recursion, and UID/GID shifting.

Key local helpers:

- `help()` and `version()` print command usage and package version.
- `parse_chunk_sizes()` accepts `auto`, an average size, or `min:avg:max`; it enforces `CA_CHUNK_SIZE_LIMIT_MIN` and `CA_CHUNK_SIZE_LIMIT_MAX`.
- `parse_what_selector()` maps `--what=` to archive, archive index, blob, blob index, or directory modes.
- `parse_argv()` parses all global options with `getopt_long()`, validates booleans, digest and compression names, feature flags, UID ranges, and exports selected log/verbose settings to `CASYNC_LOG_LEVEL` and `CASYNC_VERBOSE` for helper processes.
- `set_default_store()` chooses the primary chunk store from `--store`, `CASYNC_STORE`, the index locator patched to `default.castr`, or current-directory `default.castr`.
- `load_seeds_and_extra_stores()` attaches `--extra-store` and `--seed` paths to a `CaSync`; failures are logged and ignored rather than fatal.
- `combined_with_flags()` and `load_feature_flags()` merge defaults with `--with`/`--without`, exclusion flags, digest flags, UID shift/range, immutable undo, compression, and delete policy into the `CaSync`.
- `load_chunk_size()`, `verbose_print_feature_flags()`, `verbose_print_path()`, `verbose_print_done_make()`, and `verbose_print_done_extract()` provide common setup and instrumentation.
- `process_step_generic()` handles common `CaSync` step return codes, including polling via `sync_poll_sigset()`, path progress events, and not-found failures.
- `normalize_seek_path()` trims leading slashes and turns root/empty paths into no seek path.
- `mtree_escape_full()` and `mtree_escape()` emit mtree-safe octal escapes.
- `list_one_file()` formats one current entry for `list`, `mtree`, or `stat`.
- `allocate_stores()` builds arrays of `CaStore` instances for `pull` and `push`.
- `dispatch_verb()` maps the post-option argv verb to its implementation.

Primary external types used:

- `CaSync` from `casync.h` is the encode/decode state machine. The tool configures base/archive/index/store/cache/seeds, feature flags, payload/archive/hardlink digest calculation, seek paths/offsets, and extraction policies, then repeatedly calls `ca_sync_step()`.
- `CaStore` from `castore.h` is used directly for GC and remote store serving/receiving.
- `CaRemote` from `caremote.h` implements bidirectional remote protocol state for internal `pull`/`push`.
- `CaIndex` is used by `push` for incremental index reception and post-transfer installation.
- `CaBlockDevice` from `canbd.h` backs `mkdev`, serving a blob or blob index as an NBD block device.
- `CaChunkCollection` from `gc.h` tracks chunks referenced by indices for garbage collection.
- `CaChunkID`, digest, compression, archive feature flags, and protocol constants come from the `ca*` format/protocol headers.

## Control Flow

`main()` disables SIGPIPE, parses global arguments, installs the exit handler, dispatches the verb with `argc - optind`, then restores the handler and frees global strings/vectors. Negative returns become `EXIT_FAILURE`; zero and positive returns become success.

`verb_make()` creates archives (`.catar`), archive indices (`.caidx` plus chunk store), or blob indices (`.caibx`). It infers operation from `--what`, output suffix, and input `stat()` mode. Directory input maps to archive/archive-index; regular file or block-device input maps to blob-index. It creates an encode `CaSync`, configures input base fd, archive or index output, optional store, feature flags, chunk sizes, rate limits, logging, and optional archive cache. The loop calls `ca_sync_step()` until `CA_SYNC_FINISHED`, where it prints verbose statistics and the archive digest if available. File progress events are shown as packing/packed.

`verb_extract()` decodes `.catar`, `.caidx`, or `.caibx` into a directory, file, block device, or stdout. It infers operation from `--what`, input suffix, and output `stat()` mode. Archive and archive-index default to output `.`; blob extraction defaults to stdout if no output is supplied. For indexed inputs it derives a default store and optionally adds the existing output as an implicit seed. It supports subtree extraction through `ca_sync_seek_path()` using a boundary fd/path. The decode loop handles `CA_SYNC_FINISHED`, progress events, remote polling, and verbose feature/stat reporting.

`verb_list()` powers `list`, `mtree`, and `stat`. It can inspect a local directory by encoding it, or inspect an archive/archive-index by decoding it. For archive-index input it configures a default store. Payload reads are disabled for ordinary listing, but `mtree` and `stat` enable payload digests, and `stat` also enables hardlink digests. On `CA_SYNC_NEXT_FILE`, `list_one_file()` prints the entry. For `mtree`, regular-file digest output is deferred until `CA_SYNC_DONE_FILE`; for `stat`, non-directory digest/hardlink digest output is printed at done-file and then returns.

`verb_digest()` computes a digest for a directory, blob, archive, archive index, or blob index. Local directories and local blob files use an encode `CaSync`; archives and indices use a decode `CaSync`. It enables archive digest calculation. If a seek path points to a regular file inside an archive, it switches to payload digest output for that file; if it points to a directory, it emits the archive digest for the subtree.

`verb_mount()` is compiled only with FUSE support. It decodes an archive or archive index as a directory and hands the configured `CaSync` to `ca_fuse_run()`, with optional mount-directory creation controlled by `--mkdir`.

`verb_mkdev()` decodes a blob or blob index as a regular-file stream and exposes it as an NBD device. It first steps the `CaSync` until archive size is known, opens an NBD block device rounded up to 512-byte size, optionally waits for udev initialization, emits sd_notify readiness with the device path, and then services block requests by seeking the `CaSync` to the requested offset and collecting `CA_SYNC_PAYLOAD` data. EOF before a full request is zero-filled. Optional user-provided names are interpreted as explicit NBD devices, `/dev` friendly names, or symlink paths; created symlinks are removed on finish.

`verb_pull()` is an internal server-side remote verb used over stdio. It advertises readable store/index/archive capabilities, sets archive/index paths and readable stores, steps `CaRemote`, responds to chunk requests from configured stores with either chunk data or missing markers, and polls with signal-aware handling when idle. Pulling from base/archive as a source is explicitly not supported when `base_path` is set.

`verb_push()` is the internal counterpart for receiving pushed archive/index/chunks. It advertises writable capabilities, incrementally writes the incoming index through `CaIndex`, writes archive data through `CaRemote`, stores received chunks into the writable store, and, when requested by the remote feature flags, walks the received index to request missing chunks back from the client. It sends goodbye only after expected index/archive data is written and pending chunks are drained, then installs the index.

`verb_udev()` reads `/run/casync/<device-name>` for a pretty NBD name if the file is locked by a live casync process and prints `CASYNC_NAME=...`. It is intended for udev rules rather than direct user invocation.

`verb_gc()` constructs a `CaChunkCollection` from one or more index paths, derives or validates the store, prints usage when verbose, and calls `ca_gc_cleanup_unused()` with verbose and dry-run flags.

## State And Persistence Behavior

This file's persistent outputs are produced through lower-level APIs: archive files, index files, chunk stores, cache directories, extracted trees/files/devices, installed remote indices, and GC modifications. It does not manually serialize archive structures, but its path and option choices decide what gets persisted.

Store selection is central. Indexed make/extract/list/digest/mount/mkdev flows either use `--store`, `CASYNC_STORE`, or an automatically derived sibling/default `default.castr`. Extra stores are read-only lookup sources for `CaSync`. Seeds are local paths used to avoid fetching or rewriting data; extraction may add the pre-existing output path as an implicit seed unless `--seed-output=no`.

Feature persistence is controlled through `load_feature_flags()`. Archive-producing flows default to `SUPPORTED_WITH_MASK` for directory archives, while blob index creation uses no metadata features. Options can record or suppress uid/gid width, names, timestamps, permissions, symlinks, special nodes, xattrs, ACLs, SELinux, file capabilities, quota project IDs, FAT attributes, chattr flags, btrfs flags, and digest choice. Exclusion flags for nodump, submounts, and `.caexclude` also ride in the same feature mask.

Extraction state can mutate destination trees: it may delete files absent from the archive, undo immutable flags before deletion, reflink or hardlink from seeds, punch sparse holes, and shift UID/GID values. Those behaviors are all configured here and executed in the decoder.

The `make --cache` path persists encoder cache data. With `--cache-auto`, the cache defaults to `<input>/.cacac`; archive digest calculation is disabled when a cache is used, so digest output differs from uncached make runs.

Signal handling is cooperative. The global `quit` flag from `signal-handler.h` is checked in all long loops; poll operations block/unblock the exit handler carefully. Most verbs return shutdown as failure, but `mkdev` treats user-triggered quit as a successful detachment path.

## Dependencies And Integration Points

The file is tightly integrated with:

- Archive/index/chunk semantics: `caformat.h`, `caformat-util.h`, `caindex.h`, `cachunkid.h`, digest and compression helpers.
- The synchronization engine: `casync.h` supplies all encode/decode configuration, stepping, current-entry inspection, seeking, payload retrieval, digest, cache, and runtime-stat APIs.
- Stores and GC: `castore.h` and `gc.h` handle chunk persistence and cleanup.
- Remoting: `caremote.h` and `caprotocol.h` implement the stdio protocol used by internal `pull` and `push`; `CASYNC_LOG_LEVEL`, `CASYNC_VERBOSE`, and likely `CASYNC_REMOTE_PATH` tests show helper-process integration.
- Device integration: `canbd.h` serves NBD requests; optional `libudev` and `udev-util.h` are used to wait for block device readiness and expose pretty names.
- Optional FUSE: `cafuse.h` provides mounted archive/index access when compiled with `HAVE_FUSE`.
- Systemd-style readiness: `send_notify("READY=1")` and, for NBD, `DEVICE=...`.
- Logging, parsing, utilities, and signal wrappers: `log_*`, `parse_boolean`, `parse_size`, `ca_locator_*`, `ca_strip_file_url`, `strv_*`, cleanup attributes, `safe_close`, `ppoll`, and path helpers.

## Risks And Edge Cases

Operation inference is suffix- and `stat()`-driven. Ambiguous stdin/stdout or suffix-less paths require `--what`; wrong inference can cause refusal or a different mode than the user intended.

Remote and non-local locators are accepted only in selected roles. For example, source directories and extraction outputs must be local paths, while archive/index/store locators may be auto-routed through lower-level remote support.

`load_seeds_and_extra_stores()` logs and ignores failed seed/extra-store additions. This preserves availability but can silently degrade deduplication, reflink/hardlink reuse, or fetch avoidance.

`set_default_store()` derives `default.castr` from the first index path. `gc` explicitly uses the first index to choose a single store for all supplied indices, which is risky if indices reference different stores.

`parse_what_selector()` help output omits `archive` even though `archive` is accepted; the user-facing allowed-values list can be misleading.

There are a few rough error-message details: `verb_udev()` logs `argv[2]` when `argc == 2`, which is out of range on invalid path errors; some messages use "list" language inside digest validation. These are diagnostic bugs rather than core data-path issues.

`mkdev` requires a seekable archive to determine size and assumes request serving can seek the `CaSync` to arbitrary offsets. It rounds size to 512 bytes and zero-fills past EOF, which is appropriate for block devices but should be tested against boundary cases. It also creates/removes symlinks and relies on udev/locking behavior under `/run/casync`.

Cache use disables archive digest output during `make`, so callers expecting a printed digest need to account for cache mode.

The remote `push` path writes chunks to `stores.stores[0]`; argument validation must ensure a writable store exists whenever chunk reception is possible. The code prevents "nothing to do" but its behavior depends on protocol feature negotiation and the presence of `wstore_path`.

Many command loops rely on `assert(false)` for unreachable `CaSync`/`CaRemote` states. New engine return codes must update this file or debug builds will abort and release builds may have undefined behavior after impossible-state assumptions.

## Test Signals

Existing test scripts provide high-value behavioral signals:

- `sources/sync-backup/casync/test/test-script.sh.in` covers local directory `list`, `mtree`, `digest`, archive and index `make`, archive/index inspection, extraction with seeds and hardlink toggles, subtree seeking, remote SSH-style locators via `CASYNC_REMOTE_PATH`, and HTTP archive/index reads.
- `sources/sync-backup/casync/test/test-cache.sh.in` compares list/mtree/digest behavior for cached and uncached archive-index creation across unchanged and changed source trees, exercising `--cache` and cache invalidation statistics.
- `sources/sync-backup/casync/test/test-fuse.sh.in` covers FUSE `mount` for archive indices and verifies mounted content digest against extracted content.
- `sources/sync-backup/casync/test/test-nbd.sh.in` covers blob digest, blob-index make/extract, seeded blob extraction, `mkdev`, notify readiness, block reads, and digest comparison through the NBD node.
- `sources/sync-backup/casync/test/test-casync.c` includes direct library-level `CaSync` tests that complement the CLI script coverage.

Useful additional tests for this file would target `--what` disambiguation on stdin/stdout, invalid `--chunk-size` triplets, `--uid-range=4294967296`, `--with=help`/`--what=help` output correctness, seed/extra-store failure warnings, GC with indices from different stores, `mkdev` symlink cleanup on early errors, and the `verb_udev()` invalid-argument diagnostic.
