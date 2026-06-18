# sources/user-network-fs/samba/source4/libcli/clilist.c

## Purpose

`clilist.c` implements SMB1 directory listing convenience functions. It supports modern TRANS2 find-first/find-next searches and old LANMAN search calls, normalizing returned entries into `struct clilist_file_info` and invoking a caller callback for each result.

## Important APIs, Types, and Functions

Public APIs are `smbcli_list_new()`, `smbcli_list_old()`, and `smbcli_list()`. Internal helpers are `interpret_long_filename()`, `smbcli_list_new_callback()`, `interpret_short_filename()`, and `smbcli_list_old_callback()`. `struct search_private` holds accumulated entries, counts, selected data level, last name, and old-style resume id.

## Control Flow

`smbcli_list()` selects old search for `PROTOCOL_LANMAN1` or older, otherwise new TRANS2 search. New search chooses `BOTH_DIRECTORY_INFO` when NT SMBs are available or `STANDARD` otherwise, loops first/next calls until end-of-search or zero results, accumulates entries, then calls the user callback once per accumulated entry. Old search follows the same pattern using `RAW_SEARCH_SEARCH` and resume ids.

## State and Persistence Behavior

Listing is read-only from the share perspective but may keep server-side search handles until close-if-end behavior or end of search. Locally it accumulates all entries in a talloc array before invoking callbacks, so memory use scales with result count.

## Dependencies and Integration Points

The file depends on raw search APIs, negotiated protocol/capabilities, NT time conversion, and the `clilist_file_info` contract used by delete and wildcard helpers.

## Risks and Edge Cases

Accumulating the entire result set can be expensive for large directories. In `smbcli_list_new()`, an error during a subsequent find-next returns `-1` without freeing `state.mem_ctx`. Callback invocation is deferred until after enumeration, so callers cannot stop early. Resume by last name can be fragile with changing directories.

## Test Signals

Tests should cover old and new protocol paths, large directories, Unicode/short-name entries, hidden/system attributes, changing directories during enumeration, no-match results, and callback-visible ordering/counts.
