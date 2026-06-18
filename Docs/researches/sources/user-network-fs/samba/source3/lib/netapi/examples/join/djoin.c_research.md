# sources/user-network-fs/samba/source3/lib/netapi/examples/join/djoin.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/join/djoin.c

Purpose: Demonstrates both phases of offline domain join: provisioning a computer account and requesting local offline join.

Important APIs/types/functions: Calls `NetProvisionComputerAccount()`, `netapi_save_file_ucs2()`, `netapi_read_file()`, and `NetRequestOfflineDomainJoin()`. Options include domain, machine name, save/load file, and request/provision mode.

Control flow: Parses mode and join parameters. Provision mode validates domain and machine name, requests provision text data, prints/saves it, and frees it. Request mode reads a provision blob from file and submits it to `NetRequestOfflineDomainJoin()`.

State and persistence behavior: Provision mode creates/updates domain account state and may write a local join blob. Request mode changes local machine join state for next reboot.

Dependencies and integration points: Combines the two smaller offline join examples and common file helpers.

Risks: Offline join data contains sensitive material and is written as files. Mode/argument validation is minimal.

Test signals: Provision a disposable computer account, save payload, request offline join in a controlled test machine, and verify join information after reboot.
