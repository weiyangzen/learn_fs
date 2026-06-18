## sources/user-network-fs/samba/source4/kdc/sdb_to_hdb.c

Purpose: converts Samba SDB entries into Heimdal `hdb_entry` structures, including keys, flags, events, lifetimes, etypes, key trust, certificate mappings, object SID extension, and Samba KDC context attachment.

Important APIs and functions: `sdb_flags_to_hdb_flags()` maps SDB bitfields to Heimdal HDB flags with size assertion. `sdb_salt_to_Salt()`, `sdb_key_to_Key()`, `sdb_keys_to_Keys()`, and `sdb_keys_to_HistKeys()` copy key material and key history. `sdb_event_to_Event()` copies modifier principals/times. `sdb_pub_key_to_hdb_key_trust_val()` wraps RSA public keys in SubjectPublicKeyInfo for key-trust extension. `sdb_certificate_mappings_to_hdb_ext()` converts PKINIT certificate mappings. `sdb_entry_to_hdb_entry()` performs the whole conversion, replaces HDB extensions, and attaches `samba_kdc_entry` as `h->context`.

Control flow: conversion zero-initializes the output and uses `goto error` cleanup via `free_hdb_entry()` on failures. Optional SDB fields allocate corresponding Heimdal pointers only when present. Old and older keys are added as history when kvno permits. Object SID is serialized as a string octet extension.

State and persistence: no durable writes. The output `hdb_entry` owns copied key/extension data; the attached `samba_kdc_entry` back-pointer is set so later PAC/authn code can recover DSDB metadata.

Dependencies and integration: Heimdal HDB ASN.1 types, Samba krb5 wrappers, SID formatting, SDB definitions, and PAC/KDC entry structures.

Risks: conversion handles sensitive key material and complex ASN.1 allocations. Failure cleanup must free all partially built extensions. Public-key bit/byte length conversion and certificate mapping optional fields are easy to regress. The `ske->kdc_entry = h` back-pointer creates lifetime coupling.

Test signals: existing `source4/kdc/tests/sdb_to_hdb_test.c`, entries with key history, no keys, PKINIT key trust, certificate mapping enforcement modes, SID extension, optional lifetimes, etype/session etype lists, and allocation-failure cleanup.
