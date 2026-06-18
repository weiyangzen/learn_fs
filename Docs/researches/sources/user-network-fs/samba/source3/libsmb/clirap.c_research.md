# sources/user-network-fs/samba/source3/libsmb/clirap.c

## Purpose

This file combines legacy RAP client calls with higher-level path and file information helpers. It enumerates shares and servers, changes OEM passwords, sets basic file times/attributes, queries path/file metadata, parses stream information, and handles SMB1/SMB2 differences for common metadata queries.

## Important APIs, Types, and Functions

Major APIs include `cli_RNetShareEnum()`, `cli_NetServerEnum()`, `cli_oem_change_password()`, `cli_setpathinfo_ext()`, `cli_setfileinfo_ext[_send/_recv]`, `cli_qpathinfo2[_send/_recv]`, `cli_qpathinfo3()`, `cli_qpathinfo_streams[_send/_recv]`, `parse_streams_blob()`, `cli_qfileinfo_basic[_send/_recv]`, `cli_qpathinfo_basic[_send/_recv]`, and `cli_qpathinfo_alt_name()`. Helper `prep_basic_information_buf()` constructs the 40-byte `FILE_BASIC_INFORMATION` payload.

## Control Flow

RAP calls build old LANMAN parameter descriptors and use `cli_trans()` to `\\PIPE\\LANMAN`. `cli_NetServerEnum()` loops `RAP_NetServerEnum2` then `RAP_NetServerEnum3`, using the last returned server name as continuation and skipping repeated first entries. Metadata setters choose SMB2 set-info or SMB1 `cli_setfileinfo`/`cli_setpathinfo`. `cli_qpathinfo2_send()` requests all information; if the file is a reparse point it chains `cli_get_reparse_data_send()` and maps symlink/NFS reparse tags to POSIX modes.

## State and Persistence Behavior

RAP enumeration is read-only; OEM password change mutates account credentials remotely using LanMan hash and ARCFOUR-derived password buffers. Set-path/file-info calls persist timestamp and attribute changes. Query helpers hold transient parsed timestamps, sizes, inode/file ids, stream arrays, and mode classifications.

## Dependencies and Integration Points

The file depends on RAP generated constants, GnuTLS crypto, libcli auth hash helpers, reparse parsing, SMB2 fnum helpers, Trans2 constants, and lower-level qpath/qfile/fsctl helpers declared in `clirap.h` and implemented elsewhere. It is a central compatibility layer for callers that want one API across SMB1 and SMB2.

## Risks and Test Signals

Risks include RAP converter offset mistakes, fixed stack parameter buffers, legacy password crypto failures, parsing stream record lengths, reparse fetch failures after metadata queries, and SMB1 fallback paths for Win95/LANMAN dialects. Tests should cover large share/server enumerations with `ERRmoredata`, malformed comments, too-long usernames, SMB1 and SMB2 qpathinfo on normal files and symlinks, unknown reparse tags, alternate-name conversion, and stream blobs with bad next offsets.
