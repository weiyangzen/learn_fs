<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.c -->
# sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.c

## Purpose

`smb2_fio.c` adapts libsmb2 to the PS2 IOP filesystem device interface. It registers an `smb` filesystem driver, maintains a list of connected SMB shares presented as `smb:/<name>/...`, translates IOP file and directory operations into synchronous libsmb2 calls, and exposes a devctl connect operation.

## Important APIs, Types, And Functions

Public driver entry points include `SMB2_initdev`, `SMB2_init`, `SMB2_deinit`, `SMB2_devctl`, `SMB2_open`, `SMB2_close`, `SMB2_read`, `SMB2_write`, `SMB2_lseek`, `SMB2_lseek64`, `SMB2_dopen`, `SMB2_dclose`, `SMB2_dread`, `SMB2_getstat`, `SMB2_mkdir`, `SMB2_rmdir`, `SMB2_remove`, `SMB2_rename`, and `SMB2_chdir`. Internal structures are `smb2_share_list`, `dir_fh`, and `file_fh`.

## Control Flow

`SMB2_initdev` replaces any existing `smb` driver and registers `smb2man_ops`. `SMB2_devctl` locks a global semaphore and handles `SMB2_DEVCTL_CONNECT`, which creates a libsmb2 context, parses the URL, sets password, connects to the share, and prepends it to the global share list. Path operations call `prepare_path`, split the mounted share name with `find_context`, then lock around libsmb2 calls. Directory root entries can enumerate mounted shares; subdirectories use `smb2_opendir` and `smb2_readdir`.

## State And Persistence Behavior

State is process-resident in global `shares`, `smb2_curdir`, optional debug log context/file, and `smb2man_io_sema`. No durable state is written except optional debug logging to an SMB URL when compiled with `DEBUG`. File handles store libsmb2 context/file-handle pairs in `iop_file_t.privdata`.

## Dependencies And Integration Points

The file depends on PS2SDK IOP headers, IOMANX device structures, thread semaphores, `ps2smb2.h`, and public libsmb2 APIs. It is started by `smb2man.c` and exposed to PS2 software through the `smb:` device name.

## Risks And Edge Cases

`find_context` appears to return a share when `strcmp(share->name, path)` is nonzero, which means the first non-matching share is selected rather than the matching one. `SMB2_dopen` marks virtual root handling as TODO but still calls `find_context`, so mounted-share enumeration is hard to reach unless paths split as expected. Connect failure logs call `smb2_get_error(share->smb2)` after destroying the context. The share list and `smb2_curdir` are not fully cleaned up on deinit, connect does not reject duplicate names, and writes exist despite `SMB2_open` refusing non-read-only opens. `calloc` in `smb2man.c` does not check malloc failure before `memset`, which affects this file's allocations.

## Test Signals

PS2-side tests should cover connect, duplicate share names, root directory listing, path normalization for `/./`, `/..`, and backslashes, open/read/close, directory read/stat conversion, rename across shares, semaphore serialization, deinit cleanup, and failures from URL parsing or SMB connection. A focused unit test should expose the `strcmp` polarity in `find_context`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.c -->
