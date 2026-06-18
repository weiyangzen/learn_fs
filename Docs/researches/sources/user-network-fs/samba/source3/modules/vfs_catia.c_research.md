# sources/user-network-fs/samba/source3/modules/vfs_catia.c

## Purpose
`vfs_catia.c` maps filenames between Windows-visible names and Unix backing-store names for applications such as CATIA that use characters forbidden by Windows clients. It is a broad VFS wrapper that applies configured character mappings to pathname arguments, stream names, xattr names, DFS paths, and the `files_struct` names used by fd-oriented operations.

## Important APIs, types, and functions
- `struct share_mapping_entry` caches parsed `catia:mappings` for global and per-share configuration.
- `struct catia_cache` stores original and mapped `files_struct` `base_name` pointers, alternate stream base names, and recursion state.
- `init_mappings()` loads and caches share-level mappings, falling back to global mappings.
- `catia_string_replace_allocate()` delegates to `string_replace_allocate()` for `vfs_translate_to_unix` and `vfs_translate_to_windows` directions.
- `catia_translate_name()` provides the VFS translate-name hook and returns mapped names when lower modules do not.
- `CATIA_FETCH_FSP_PRE_NEXT()` and `CATIA_FETCH_FSP_POST_NEXT()` temporarily replace `fsp->fsp_name->base_name` with the Unix-mapped name before fd-based downstream calls, then restore it.
- Direct pathname wrappers cover open, rename, stat/lstat/fstatat, unlink, lchown, mkdir, chdir, realpath, xattr names, DFS paths, and stream info.
- Fd-based wrappers cover read/write, async read/write, fsync, fstat, truncate, fallocate, locks, sharemode, leases, ACLs, DOS attributes, compression, and fsctl.
- `vfs_catia_init()` registers the module as `catia` and creates a custom debug class.

## Control flow
On connect, the module disables `smbd async dosmode` because it does not provide async DOS attribute fetch hooks. For path operations, the usual flow is to map the incoming Windows-visible `base_name` to the Unix backing name, create a temporary `smb_filename`, and delegate to the next VFS module. Directory and fd-based operations are harder because downstream modules inspect the existing `files_struct`; `catia_fetch_fsp_pre_next()` creates or validates an fsp extension, stores original pointers, swaps in mapped pointers, and marks the cache busy. The post hook restores original pointers and clears the busy marker. Recursion is explicitly detected; validated recursive calls can reuse the mapped state, while changed names force a temporary cache.

Stream handling gets special treatment. `catia_fstreaminfo()` maps the base path to Unix for the lower stream query, then maps each returned stream name back to the Windows-visible form while preserving `:$DATA` suffixes. Async pread/pwrite/fsync keep the mapped fsp state active until the lower async request completes, then restore in the completion callback before marking the request done.

## State and persistence behavior
Mappings are cached in the static `srt_head` list for the lifetime of the process. Per-open-file mapping state lives in VFS fsp extensions and is removed with the fsp. No separate metadata is persisted; the backing filesystem sees mapped Unix names, and SMB clients see reverse-mapped Windows names. The module can make durable name changes through create, rename, link, symlink, DFS, xattr, and stream operations.

## Dependencies and integration points
The module depends on Samba's VFS dispatch layer, fsp extensions, `string_replace.h`, talloc, tevent request APIs, ACL/DOS attribute hooks, and path helpers. `vfs_fruit.c` comments explicitly mention using CATIA mappings for Apple illegal character handling, and `wscript_build` registers `vfs_catia`.

## Risks and edge cases
- The module relies on pointer identity in `files_struct` names to validate cache safety; external mutation of those pointers can force cache recreation or trigger panic paths.
- Async operations must restore mapped fsp names exactly once after lower completion; mistakes can leak Unix names into SMB-facing state.
- Share/global mapping cache is static and not invalidated on runtime configuration changes.
- Mapping collisions are possible if two Windows-visible names map to the same Unix name or vice versa.
- Disabling async DOS mode is necessary for correctness but can affect performance.
- Many VFS operations are wrapped; any new operation that uses names but is not added here can bypass translation.

## Test signals
No dedicated CATIA tests were found in this subset. High-value tests should configure representative `catia:mappings`, create and list names containing Windows-forbidden characters, exercise rename/link/symlink/streams/xattrs/ACLs/DOS attributes, cover alternate streams, and force nested VFS calls to validate recursion protection. Build registration and the `vfs_fruit.c` integration note are static signals.
