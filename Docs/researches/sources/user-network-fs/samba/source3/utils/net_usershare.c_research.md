# sources/user-network-fs/samba/source3/utils/net_usershare.c

## Purpose
Implements local `net usershare` add/delete/info/list for user-defined share files under the configured usershare directory.

## Important APIs, Types, and Functions
`get_basepath()` resolves `lp_usershare_path()`. `get_share_list()` scans regular usershare files, filtering by wildcard and owner. `info_fn()` opens files, validates them with `parse_usershare_file()`, and prints list/info output. `net_usershare_add()` validates names, paths, owner policy, ACLs, guest policy, then writes a version-2 share file through `mkstemp()`, `fchmod()`, `write()`, and atomic `rename()`. Name/SID conversion uses `netlookup.c` helpers.

## Control Flow
`net_usershare()` rejects disabled usershares and inaccessible directories, then dispatches subcommands. Add parses positional args, applies defaults, enforces max count, validates absolute directory path and ownership policy, canonicalizes ACL entries to SIDs, writes a protected temp file, and renames it into place. Delete validates and unlinks. Info/list scan matching files and reuse the parser/renderer.

## State and Persistence
Persistent state is one regular file per usershare in `lp_usershare_path()`. Add/modify replaces definitions atomically; delete unlinks them. Info/list are read-only.

## Dependencies and Integration Points
Depends on loadparm usershare settings, filesystem wrappers, usershare parser/security descriptors, local SID/name lookup, and common net options like `--long`.

## Risks
Security-sensitive because configured non-root users can publish shares. The code mitigates symlink/race problems with regular-file checks, `O_NOFOLLOW` for reads where available, temp files, and atomic rename. Maximum-share counting is advisory and races. ACL name conversion depends on local smbd/LSA availability.

## Test Signals
Cover disabled/missing directory, invalid names, Unix-user name collision, relative/non-directory paths, owner-only rejection, guest disallowed, malformed ACLs, SID and name ACL conversion, atomic replace, delete failure, wildcard list/info, malformed files, and non-regular file skips.
