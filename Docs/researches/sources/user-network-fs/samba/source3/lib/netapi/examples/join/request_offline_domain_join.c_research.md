# sources/user-network-fs/samba/source3/lib/netapi/examples/join/request_offline_domain_join.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/join/request_offline_domain_join.c

Purpose: Demonstrates applying offline domain join data through `NetRequestOfflineDomainJoin()`.

Important APIs/types/functions: Reads a provision blob using `netapi_read_file()`, then calls `NetRequestOfflineDomainJoin(provision_bin_data, provision_bin_data_size, flags, NULL)`.

Control flow: Parses `--loadfile` and optional flags, requires the file, loads it into memory, submits the request, reports errors, frees context, and exits.

State and persistence behavior: Changes local machine join configuration using supplied provision data; no new local output is written.

Dependencies and integration points: Consumes data from `provision_computer_account` or `djoin`.

Risks: The payload is sensitive and must match the target machine/domain. Read size is stored in `uint32_t`.

Test signals: Apply a known-good test payload and verify domain membership after required reboot.
