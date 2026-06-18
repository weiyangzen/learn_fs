# sources/user-network-fs/samba/source4/libcli/raw/clioplock.c

Purpose: raw SMB client helpers for oplock break handling.

Important APIs: `smbcli_oplock_ack()` sends a one-way `SMBlockingX` oplock release acknowledgement; `smbcli_oplock_handler()` installs the transport-level oplock break callback and private data.

Control flow: ack constructs a locking request with command `SMBlockingX`, `LOCKING_ANDX_OPLOCK_RELEASE`, target file number, and requested ack level, then sends it without waiting for a normal response. Handler setup simply stores callback fields in the transport.

State and persistence: callback state lives in `transport->oplock`; ack changes remote server oplock state. No local persistence.

Dependencies and integration: depends on raw request setup/send and `clitransport.c` break dispatch, which listens for MID `0xFFFF` break packets when a handler is installed.

Risks: ack is one-way and returns only send success; server acceptance is not observed. Incorrect ack level or file number can affect cache consistency. Test signals include break callback installation, receipt of break packets, ack wire fields, and missing-handler logging.
