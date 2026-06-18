<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawsearch.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawsearch.c

Purpose: `rawsearch.c` implements raw SMB directory enumeration for old search commands and trans2 findfirst/findnext/findclose. It parses many search data levels and streams entries to a caller callback.

Important APIs, types, and functions: Main entry points are `smb_raw_search_first`, `smb_raw_search_next`, and `smb_raw_search_close`. Shared parser `smb_raw_search_common` handles SMB/SMB2-style directory info records. Local helpers include old search first/next/close, trans2 first/next blob calls, `parse_trans2_search`, `smb_raw_search_backend`, and `smb_raw_t2search_backend`.

Control flow: Old search paths build `SMBsearch`, `SMBffirst`, or `SMBfunique` requests, append ASCII patterns and resume var blocks, then parse fixed 43-byte records. Trans2 paths build `TRANSACT2_FINDFIRST` or `TRANSACT2_FINDNEXT`, optionally encode EA name lists, receive parameter/data blobs synchronously, validate parameter sizes, store returned handle/count/end flags, then parse each data record until count, callback stop, parse error, or zero next offset. Close uses old `SMBfclose` or `SMBfindclose`.

State and persistence behavior: The file does not keep local persistent state; search continuation state is carried by server handles or old resume IDs in caller-provided unions. Server-side directory search handles are opened by findfirst and closed by findclose or exhaustion. Parsed names/EAs are allocated under the caller context and passed to callbacks.

Dependencies and integration points: It depends on raw trans2 helpers, EA name/list helpers, DOS/NT time helpers, raw string/blob parsing, and the callback type from `interfaces.h`. `libcli/clilist.c`, NTVFS CIFS passthrough, nbench, Unix extension tests, and raw search torture tests consume it.

Risks: Search parsing is offset-heavy and level-specific. Some legacy formats use 8-bit name lengths and optional resume keys; incorrect flags shift all fields. The callback may stop early without closing server handles, so callers must manage findclose when needed. SMB2 search level is rejected here even though common parsers support SMB2-like records. Malformed next offsets return invalid-parameter rather than partial results.

Test signals: `source4/torture/raw/search.c`, Unix info2 search tests, chkpath/listing tests, and nbench directory enumeration are key signals. Coverage should include every data level, EA-list search, resume-key flags, ASCII vs Unicode negotiation, callback early termination, malformed next offsets, old search resume IDs, and findclose behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawsearch.c -->
