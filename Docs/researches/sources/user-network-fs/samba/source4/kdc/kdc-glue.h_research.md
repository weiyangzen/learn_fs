# sources/user-network-fs/samba/source4/kdc/kdc-glue.h

## Purpose
`kdc-glue.h` is the shared KDC glue header that binds Samba KDC code to Heimdal HDB/KDC plugin types and exposes HDB construction, request audit helpers, PAC checksum verification, and device PAC retrieval.

## Important APIs, Types, And Functions
It includes Kerberos, Heimdal HDB, Heimdal KDC plugin, Samba KDC, and KDC server headers. It declares `hdb_samba4_create_kdc`, `hdb_samba4_kpasswd_create_kdc`, `hdb_samba4_set_ntstatus`, audit-info setters for client/server, `kdc_check_pac`, and `samba_kdc_get_device_pac`.

## Control Flow
The header has no runtime flow. It defines the cross-file contract used by the Heimdal service startup, HDB plugin, PAC glue, and kpasswd service.

## State And Persistence Behavior
No state is stored in the header. It exposes pointers to opaque Samba KDC contexts and Heimdal request objects whose lifetimes are managed by implementation files.

## Dependencies And Integration Points
This header is a central integration point for `hdb-samba4.c`, `hdb-samba4-plugin.c`, `kdc-heimdal.c`, `kdc-glue.c`, and PAC/kpasswd code. Because it pulls in Heimdal headers, ABI changes in Heimdal can surface through this contract.

## Risks
Prototype drift or include-order changes can break both in-process KDC and keytab/kpasswd builds. The audit helpers transfer ownership of talloc data, so callers must understand the steal semantics declared here.

## Test Signals
Build coverage across Heimdal-enabled configurations is the main signal. Runtime signals are successful HDB creation, kpasswd keytab lookup, PAC validation, and audit info propagation through KDC requests.
