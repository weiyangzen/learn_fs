# sources/user-network-fs/samba/source3/torture/test_buffersize.c

## Purpose
`test_buffersize.c` is a small regression/stress test for `cli_qpathinfo` response buffer sizing. It repeatedly queries root path information with receive buffer sizes from 0 to 499 bytes.

## Important APIs, types, and functions
The exported function is `run_qpathinfo_bufsize`. It opens a torture connection and calls `cli_qpathinfo` with `SMB_FILE_ALL_INFORMATION`, variable `max_data_bytes`, and output pointers for returned data length.

## Control flow
The test prints a start banner, opens one SMB connection, loops `i = 0..499`, and issues `cli_qpathinfo(cli, cli, "\\", SMB_FILE_ALL_INFORMATION, 0, i, &rdata, &num_rdata)`. It ignores individual statuses and returns success if setup and loop completion succeed.

## State and persistence behavior
No server state is intentionally changed. Returned buffers are allocated by the client stack under the passed talloc context and are transient.

## Dependencies and integration points
It depends on Samba client RAP/TRANS2 qpathinfo code and is registered in the torture harness through `proto.h`.

## Risks and test signals
The value is in memory-safety and truncation behavior rather than semantic pass/fail per request. Crashes, leaks, or invalid buffer handling in `cli_qpathinfo` are the expected regression signals.
