# sources/user-network-fs/samba/source3/libsmb/clirap.h

## Purpose

This header declares the public client RAP and metadata-query APIs implemented primarily by `clirap.c` and related lower-level files. It gives other libsmb components one include for share/server enumeration, password change, path/file info, streams, flush, shadow-copy data, and FSCTL operations.

## Important APIs, Types, and Functions

The declarations cover synchronous RAP calls (`cli_RNetShareEnum`, `cli_NetServerEnum`, `cli_oem_change_password`), extended setters (`cli_setpathinfo_ext`, `cli_setfileinfo_ext_*`), metadata queries (`cli_qpathinfo2`, `cli_qpathinfo3`, `cli_qfileinfo_basic`, `cli_qpathinfo_basic`, `cli_qpathinfo_alt_name`), stream parsing (`parse_streams_blob`), lower-level `cli_qpathinfo`/`cli_qfileinfo`, `cli_flush`, `cli_shadow_copy_data`, and `cli_fsctl`.

## Control Flow

There is no runtime control flow in the header. Its design mirrors Samba's async convention: `_send()` creates a `tevent_req`, `_recv()` extracts results, and a synchronous wrapper exists for many operations.

## State and Persistence Behavior

The header stores no state. It defines ownership expectations through `TALLOC_CTX *mem_ctx` result parameters and through `DATA_BLOB` output for FSCTL.

## Dependencies and Integration Points

It forward-declares `struct cli_state` and expects included Samba headers to provide `NTSTATUS`, `TALLOC_CTX`, `struct tevent_context`, `struct tevent_req`, `SMB_STRUCT_STAT`, `SMB_INO_T`, `fstring`, `DATA_BLOB`, and `struct stream_struct`. `clisymlink.c`, `cliprint.c`, Python bindings, and other libsmb files use these declarations.

## Risks and Test Signals

The main risk is declaration/implementation drift because several declarations are implemented outside `clirap.c` in `clifile.c`. Build tests should compile consumers after signature changes, and ABI/API tests should verify async recv ownership and nullable output parameters.
