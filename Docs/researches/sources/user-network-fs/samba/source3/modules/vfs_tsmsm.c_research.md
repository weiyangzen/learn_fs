# sources/user-network-fs/samba/source3/modules/vfs_tsmsm.c

## Purpose

`vfs_tsmsm.c` integrates Samba with Tivoli Storage Manager Space Management through DMAPI. It detects migrated/offline files, advertises remote-storage capabilities, forces asynchronous I/O heuristically for possibly offline files, sends client notifications when I/O brings files online, and optionally invokes an HSM script to mark files offline. The module registers as `tsmsm` and is compiled only when DMAPI support is available.

## Important APIs, Types, And Functions

`struct tsmsm_struct` stores `online_ratio`, `hsmscript`, `attrib_name`, and optional `attrib_value`. `tsmsm_connect()` initializes this config from parameters `tsmsm:hsm script`, `tsmsm:online ratio`, `tsmsm:dmapi attribute`, and `tsmsm:dmapi value`, and requires an available DMAPI session. `tsmsm_is_offline()` is the core detector: it first uses block-count heuristics, then queries DMAPI attributes when a file may be migrated. `tsmsm_aio_force()` uses the same heuristic to decide whether I/O should be forced asynchronous.

I/O wrappers include sync and async `pread`/`pwrite`, `sendfile`, and receive callbacks that notify clients when a previously offline-looking file was accessed successfully. Attribute wrappers include `tsmsm_fget_dos_attributes()` and `tsmsm_fset_dos_attributes()`. `tsmsm_set_offline()` executes the configured script using `smbrun()`. `tsmsm_fs_capabilities()` adds `FILE_SUPPORTS_REMOTE_STORAGE` and `FILE_SUPPORTS_REPARSE_POINTS`.

## Control Flow

Connect delegates to the next VFS connect, allocates config, validates DMAPI session availability, reads configuration, and stores handle data. Offline detection first compares `512 * st_blocks` to `st_size * online_ratio`; sufficiently allocated files are assumed online. Sparse or low-block files trigger DMAPI path handling under `become_root()`: convert path to DMAPI handle, query the configured attribute, recreate a stale session on `EINVAL`, and decide offline based on attribute existence or exact configured value.

Before I/O, `tsmsm_aio_force()` cheaply decides if a file may be offline. After successful reads/writes that started from a possibly offline file, the module sends `NOTIFY_ACTION_MODIFIED | NOTIFY_ACTION_DIRLEASE_BREAK` with `FILE_NOTIFY_CHANGE_ATTRIBUTES` so clients can refresh offline status. `sendfile` is rejected with `ENOSYS` for possibly offline files to avoid blocking/non-AIO recall behavior. Setting DOS attributes delegates first, then may invoke the HSM script to offline the file.

## State And Persistence

The module keeps per-handle configuration only. Persistent state is external: DMAPI-managed file migration attributes and any effects of the configured HSM script. Notifications are transient SMB state changes.

## Dependencies And Integration Points

The file requires `USE_DMAPI` and includes platform-specific DMAPI headers from XFS, AIX/JFS, or system locations. It uses Samba DMAPI session helpers, root privilege transitions, `get_full_smb_filename()`, `notify_fname()`, VFS async I/O, DOS attribute hooks, and capability hooks. Build integration appears as `vfs_tsmsm` in `source3/modules/wscript_build`.

## Risks And Edge Cases

DMAPI calls require elevated privileges and can be slow, so the heuristic is important but can misclassify sparse online files as possibly offline. On DMAPI path-to-handle failure, the module assumes offline, which favors recall safety but can affect client behavior. The HSM script command is built with shell quoting around only the path argument and uses `smbrun()`, so script path configuration must be trusted. A stale DMAPI session is retried, but repeated DMAPI failures can produce conservative offline decisions. `tsmsm_fset_dos_attributes()` appears to call `tsmsm_set_offline()` unless a specific old/new offline-bit condition returns early, so behavior should be verified against intended offline transition semantics.

## Test Signals

Tests need a DMAPI-capable filesystem or mocks for session, handle, and attribute calls. Key scenarios are online-ratio fast path, DMAPI attribute existence and value matching, stale-session recreation, sendfile rejection for possible offline files, notifications after successful recall-triggering I/O, DOS offline attribute reporting, HSM script invocation, and capability bit advertisement.
