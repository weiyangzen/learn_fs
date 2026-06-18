<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.h -->
# sources/user-network-fs/samba/source3/utils/clirap2.h

## Purpose
`clirap2.h` declares the public client RAP helper functions implemented in `clirap2.c`.

## Important APIs, types, and functions
- Forward declarations for `rap_group_info_1`, `rap_user_info_1`, and `rap_share_info_2` keep callers independent of full RAP struct definitions.
- Group, user, file, share, server, print queue, service, session, and connection functions expose legacy remote administration operations over an existing `struct cli_state`.
- Callback-heavy enum/get-info functions return decoded RAP records to caller-supplied function pointers.

## Control flow
The header has no runtime control flow. It defines call signatures used by utility modules, especially `net rap` helpers, to route decoded RAP records into display or command-specific callbacks.

## State and persistence behavior
State is external: callers provide an authenticated SMB client connection and callbacks. Functions may mutate remote server administrative state depending on the operation.

## Dependencies and integration points
The header includes `../libsmb/clirap.h` for `struct cli_state` and related client definitions. It is a bridge between Samba utility code and low-level RAP marshalling in `clirap2.c`.

## Risks and edge cases
- Many callbacks use long positional parameter lists, making accidental argument order mistakes easy.
- Most functions return integer RAP result codes rather than `NTSTATUS`, so callers must interpret legacy error values correctly.
- Header/API stability matters because multiple `net` modules may include it.

## Test signals
Build coverage of `net` RAP utilities and successful remote RAP integration commands validate this interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.h -->
