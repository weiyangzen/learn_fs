# sources/user-network-fs/samba/source3/libsmb/clilist.c

## Purpose

This file implements directory enumeration for SMB clients across old SMB search, SMB1 Trans2 find, and SMB2 find paths. It normalizes returned directory entries into `struct file_info`, validates server-returned names, and offers both async one-entry-at-a-time iteration and a synchronous callback wrapper.

## Important APIs, Types, and Functions

Key APIs are `is_bad_finfo_name()`, `cli_list_send()`, `cli_list_recv()`, `cli_list()`, and legacy `cli_list_old()`. Internal parsers include `interpret_short_filename()`, `interpret_long_filename()`, and `calc_next_entry_offset()`. State structs `cli_list_old_state`, `cli_list_trans_state`, and `cli_list_state` track search masks, Trans2 handles, resume keys, raw last names, accumulated `file_info` arrays, and per-entry delivery progress.

## Control Flow

`cli_list_send()` chooses SMB2 listing, SMB1 Trans2 find, or old `SMBsearch` based on dialect. The Trans2 path sends `FINDFIRST`, parses returned records according to the requested info level, stores entries, then sends `FINDNEXT` using resume key and last filename bytes until end-of-search. The old path loops `SMBsearch` and finally closes with `SMBfclose`. `cli_list_recv()` can be called repeatedly; it moves one `file_info` to the caller and defers the request callback so async consumers receive entry notifications.

## State and Persistence Behavior

No persistent filesystem state is modified. Client-side state includes accumulated directory entries, raw resume names, old-search status bytes, and protocol search handles. The code disconnects the SMB connection if a server returns names containing `/` or, for Windows pathnames, `\`, treating such names as hostile network responses.

## Dependencies and Integration Points

The file integrates with `cli_smb2_list_*`, `cli_trans`, `cli_smb_send`, DFS path rewriting through `smb1_dfs_share_path()`, time conversion helpers, Trans2 info-level constants, and `dir_check_ftype()` for SMB2-side attribute filtering. Higher-level file, tree, and client tools consume `cli_list()` for wildcard scans.

## Risks and Test Signals

Important risks are malformed record offsets, name-length overrun, Unicode conversion failures, looping `FINDNEXT` responses, and mismatched SMB2 attribute filtering semantics. Tests should inject truncated old-search records, invalid next offsets, bad short-name lengths, unsafe separators, repeated resume names, empty matches, SMB2 no-more-files behavior, and callback errors stopping iteration.
