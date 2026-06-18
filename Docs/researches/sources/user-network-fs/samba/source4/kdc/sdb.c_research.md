## sources/user-network-fs/samba/source4/kdc/sdb.c

Purpose: memory management and encryption-type derivation for Samba's intermediate SDB entry representation.

Important APIs and functions: `sdb_key_free()`, `sdb_keys_free()`, `sdb_pub_key_free()`, `sdb_pub_keys_free()`, `sdb_certificate_mapping_free()`, `sdb_certificate_mappings_free()`, and `sdb_entry_free()` recursively free and zero SDB structures. `sdb_entry_set_etypes()` derives current etype list from key keytypes. `sdb_entry_set_session_etypes()` builds preferred session etype lists in AES256, AES128, RC4 order based on requested booleans.

Control flow: free helpers tolerate NULL, clear sensitive keyblock contents via krb5 APIs, free principal fields with NULL context, and reset structs after release. Etype setters allocate only when corresponding input exists/flags are requested.

State and persistence: SDB entries are transient conversion objects populated from DSDB. Freeing an SDB entry also detaches and frees its `samba_kdc_entry`, clearing back-pointers.

Dependencies and integration: used by DB fetchers and conversion files (`sdb_to_hdb`, `sdb_to_kdb`) before presenting data to Heimdal/MIT.

Risks: key material zeroing depends on correct helper use. Session etype order influences negotiated service ticket session keys. Attached `samba_kdc_entry` lifetime must not outlive the converted KDC entry incorrectly.

Test signals: free fully and partially populated entries, valgrind/asan leak checks, etype derivation from multi-key accounts, session etype ordering, and double-free resistance through zeroing.
