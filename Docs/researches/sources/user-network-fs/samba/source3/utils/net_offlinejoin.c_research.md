# sources/user-network-fs/samba/source3/utils/net_offlinejoin.c

## Purpose
This file implements `net offlinejoin`, covering offline domain join provisioning, applying an ODJ blob, and composing an ODJ blob from supplied domain and machine-account data.

## Important APIs, Types, And Control Flow
`net_offlinejoin()` prints usage, initializes libnetapi, and dispatches textual commands `provision`, `requestodj`, and `composeodj`. `net_offlinejoin_provision()` parses `domain=`, `machine_name=`, optional OU/DC/default-password/reuse/save/print options, calls `NetProvisionComputerAccount()`, and optionally writes UTF-16LE-with-BOM ODJ text. `net_offlinejoin_requestodj()` reads ODJ data from `loadfile=` or stdin (`-i`), strips a trailing newline, and calls `NetRequestOfflineDomainJoin()`. `net_offlinejoin_composeodj()` collects realm, workgroup, credentials, DC name/IP, domain SID/GUID, forest, and AD/NT4 flag, validates them, calls `NetComposeOfflineDomainJoin()`, then saves and/or prints the resulting blob.

## State And Persistence
Provisioning creates or reuses a machine account through NetAPI and may save an ODJ file. Requesting an ODJ applies provisioning data to local machine state through NetAPI. Compose only emits a blob unless saved. File writes use `file_save()` after registry string conversion with `push_reg_sz()`.

## Dependencies And Integration Points
It depends on libnetapi, Samba credentials, command-line helpers, registry string utilities, SID/GUID parsing, file load/save helpers, and `struct net_context` options such as realm, workgroup, host, destination IP, password, and stdin mode.

## Risks And Test Signals
Top-level dispatch uses independent `if` statements and returns success for unknown commands after libnetapi initialization, which is a CLI correctness risk. `requestodj` strips the last byte before checking for zero size if stdin produced an empty buffer. Saved blobs intentionally use UTF-16LE plus BOM for Windows compatibility. Test all required argument validation, unknown command behavior, savefile/printblob combinations, IPv4/IPv6 DC address formatting, stdin and loadfile paths, NetAPI error propagation, and restart-required status handling.
