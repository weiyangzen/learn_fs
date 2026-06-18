# sources/user-network-fs/samba/source3/libsmb/cliprint.c

## Purpose

This file implements legacy RAP/LANMAN print queue operations over `\\PIPE\\LANMAN`: enumerating print jobs and deleting a print job.

## Important APIs, Types, and Functions

The exported APIs are `cli_print_queue()` and `cli_printjob_del()`. `fix_char_ptr()` converts server pointer/converter pairs into safe offsets inside the returned RAP data buffer and substitutes `""` or `"<ERROR>"` for null or invalid pointers. Parsed queue entries are returned through `struct print_job_info` to a caller callback.

## Control Flow

`cli_print_queue()` builds a RAP parameter block for `DosPrintJobEnum` function 76, calls `cli_trans()` against `\\PIPE\\LANMAN`, checks the result code, then walks fixed-size PRJINFO_2 records. For each job it extracts id, priority, user, submitted time, size, and name, resolving string pointers through `fix_char_ptr()`. `cli_printjob_del()` sends function 81, reads the result code, and maps `ERRnosuchprintjob` to `NT_STATUS_INVALID_PARAMETER`.

## State and Persistence Behavior

Enumeration is read-only. Deletion mutates the remote print queue by cancelling a job. The file uses only transient parameter and response buffers.

## Dependencies and Integration Points

It depends on `cli_trans`, RAP format strings, `smb1cli_conn_server_time_zone()` for submitted-time conversion, fixed fstring copies, and `libsmb/clirap.h`. It is part of the old SMB1 print management surface.

## Risks and Test Signals

Risks include malformed converter offsets, truncated job records, unterminated strings, unexpected RAP result codes, and fixed 1000-byte response sizing. Tests should cover valid queues, empty queues, invalid string pointers, result-code mapping, truncated `rparam`/`rdata`, and deletion of missing jobs.
