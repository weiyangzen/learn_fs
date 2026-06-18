## sources/user-network-fs/samba/source4/kdc/pac-glue.h

Purpose: public PAC glue interface shared by Heimdal and MIT KDC integration layers.

Important types and APIs: defines `enum samba_asserted_identity`, Samba KDC PAC flags, and `struct samba_kdc_entry_pac` wrapper containing PAC pointer, PAC principal, krbtgt entry, optional local entry, and MIT-only trust boolean. Declares PAC wrapper constructors, PAC necessity and krbtgt trust checks, DB user-info fetch, policy error mapping, client-access check, PAC verify/get/update, device check, and S4U2Proxy RBCD check.

Control flow and integration: callers construct `samba_kdc_entry_pac` for client/device/delegated proxy tickets, then call verify/get/update depending on AS/TGS flow. MIT uses `samba_kdc_entry_pac_from_trusted()` because MIT lacks Heimdal's `krb5_pac_is_trusted()` API.

State and persistence: interface exposes entry-backed caches but performs no persistence in the header.

Dependencies: krb5 PAC/principal types, Samba KDC entries, auth session/audit types, NTSTATUS/WERROR mapping, and generated auth/PAC structures.

Risks: the wrapper invariants are critical: non-NULL PAC must have an associated krbtgt, and trust must be explicit on MIT. Flag meanings must remain aligned between MIT bridge and PAC glue.

Test signals: compile both Heimdal and MIT builds, construct PAC wrappers for absent PAC, trusted PAC, RODC PAC, trust PAC, and validate each public PAC operation rejects invalid wrapper combinations.
