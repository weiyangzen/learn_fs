<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_util.c -->
# sources/user-network-fs/samba/source3/auth/user_util.c

## Purpose
Provides username mapping and membership helpers for source3 authentication. It canonicalizes incoming SMB/DOS usernames into UNIX/Samba names using a configured script, username map file, in-process last-result cache, optional gencache entries, UNIX groups, and netgroups.

## APIs, Types, and Functions
Public functions are `user_in_netgroup()`, `user_in_list()`, and `map_username()`. Static helpers include `get_last_from()`, `get_last_to()`, `set_last_from_to()`, `skip_space()`, `fetch_map_from_gencache()`, and `store_map_in_gencache()`. `map_username()` accepts an input name and returns a talloc-owned output name; its boolean return indicates whether the name changed according to mapping rules.

## Control Flow, State, and Persistence
`map_username()` first copies the input to the output, then checks the process-global `last_from`/`last_to` optimization, then optional gencache using an uppercase `USERNAME_MAP/<user>` key. If `username map script` is configured, it runs the script with the user quoted as an argument, reads returned lines from the command fd, and uses the first line as the mapped name. Otherwise it opens `username map`, parses `unixname = dosnames` lines with `fgets_slash()`, trims whitespace, honors leading `!` for immediate return, builds a DOS user list, and matches either wildcard `*` or `user_in_list()`. A miss stores a self-map in the last-result cache and gencache to avoid repeated scans. Global state is `last_from`/`last_to`; durable-ish cache state is Samba gencache with `lp_username_map_cache_time()`.

## Dependencies and Integration
Depends on loadparm username-map settings, substitution context, `smbrun()`, file loading helpers, list parsing, `gencache`, UNIX group checks via `user_in_group()` from token utilities, optional libc netgroup support, and case-insensitive Samba string helpers. Kerberos and NTLM authentication paths call this once to canonicalize incoming account names before local lookup.

## Risks and Test Signals
Risks include command execution trust for the username map script, expensive or stale mappings when gencache lifetime is long, process-global last-result behavior across users, case-sensitive netgroup lookup with only lowercase retry, map-file parse edge cases, and recursive dependency where user-list group checks build tokens through token utilities. Test signals include script success/failure/no-output, map-file wildcard and `!` rules, comments and whitespace trimming, gencache disabled/enabled behavior, repeated lookup hitting last-result cache, UNIX group and netgroup membership forms (`@`, `+`, `&`, `+&`, `&+`), and unmapped names preserving the original output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_util.c -->
