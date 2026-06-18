# sources/user-network-fs/samba/source3/lib/netapi/examples/join/provision_computer_account.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/join/provision_computer_account.c

Purpose: Demonstrates generating offline-domain-join provisioning data with `NetProvisionComputerAccount()`.

Important APIs/types/functions: Accepts domain, machine name, optional machine password, OU, domain controller, reuse flag, and save file. Uses `netapi_save_file_ucs2()` for persisted payloads.

Control flow: Parses options, validates required domain/machine name, calls provisioning API, prints the returned text data, optionally writes it as UTF-16LE, frees result data, and exits.

State and persistence behavior: Creates or reuses a domain computer account and can persist sensitive provisioning text locally.

Dependencies and integration points: First half of offline domain join; feeds `request_offline_domain_join`.

Risks: Provision payload is sensitive. Reuse behavior and account password choices affect domain security.

Test signals: Provision in a test OU, inspect account creation, save payload, and use it with request/offline join tests.
