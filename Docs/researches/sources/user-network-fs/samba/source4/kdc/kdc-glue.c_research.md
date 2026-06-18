# sources/user-network-fs/samba/source4/kdc/kdc-glue.c

## Purpose
`kdc-glue.c` contains small PAC-facing helpers shared by Samba's KDC integration. It verifies PAC checksums using the right key from an HDB entry and extracts device PAC context from FAST armor state.

## Important APIs, Types, And Functions
`kdc_check_pac` maps a PAC signature checksum type to a Kerberos enctype, finds the corresponding key in an `hdb_entry` with `hdb_enctype2key`, and calls `check_pac_checksum`. `samba_kdc_get_device_pac` pulls armor client/server/PAC data from an `astgs_request_t` and packages it into `struct samba_kdc_entry_pac`.

## Control Flow
Checksum verification special-cases `CKSUMTYPE_HMAC_MD5` to RC4-HMAC, otherwise uses `krb5_cksumtype_to_enctype`. Device PAC extraction returns an all-null pac wrapper when no armor PAC exists; otherwise it retrieves the armor krbtgt Samba entry and, when locally available, the device Samba entry from HDB entry contexts.

## State And Persistence Behavior
The file does not persist state. It reads per-request armor/PAC state and HDB entry contexts created by DB glue.

## Dependencies And Integration Points
It depends on Heimdal HDB, Samba PAC utilities, NDR PAC types, `kdc/samba_kdc.h`, and request accessors from Heimdal's KDC plugin interface. It is consumed by KDC PAC verification and compound identity/device PAC handling.

## Risks
PAC checksum security depends on selecting the exact key matching the KDC signature enctype. Device PAC handling must tolerate cross-domain armor clients with no local DB entry while still requiring a local armor server entry when a PAC exists.

## Test Signals
PAC validation tests should cover RC4/HMAC-MD5 and non-RC4 checksum mappings, missing matching HDB keys, invalid signatures, FAST armor with device PAC, and cross-domain armor device entries.
