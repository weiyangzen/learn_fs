# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.c

This file implements in-memory security association management for isakmpd.

Core data structure:
- A hash table of `struct sa` lists, indexed by XOR-folded cookies and message ID.
- Initial bucket count uses `INITIAL_BUCKET_BITS`; resize code exists but is disabled.

Lookup and creation:
- `sa_init()`: allocates and initializes SA buckets.
- `sa_find()`: generic predicate scan across all buckets.
- `sa_lookup_from_icookie()`, `sa_lookup_by_name()`, `sa_lookup_by_peer()`, `sa_isakmp_lookup_by_peer()`, `sa_lookup_isakmp_sa()`, `sa_lookup_by_header()`, `sa_lookup()`: lookup SAs by cookies, message ID, peer address, name, phase, or ISAKMP SPI.
- `sa_create()`: allocates an SA from an exchange, copies cookies/message ID/DOI, initializes DOI-specific storage and proto queue, inserts into hash table, and links into the exchange SA list.
- `sa_isakmp_upgrade()`: rehashes phase 1 SA after responder cookie is known and binds transport.

Reference and lifetime management:
- `sa_enter()`, `sa_remove()`, `sa_reference()`, `sa_release()`, `sa_free()`, `sa_delete()`: manage hash membership, reference counts, protocol cleanup, timers, cert/key storage, KeyNote session, transport references, and allocated strings.
- `sa_setup_expirations()`: schedules randomized soft expiration and hard expiration timers.
- `sa_soft_expire()` and `sa_hard_expire()`: renegotiate stayalive SAs, mark fading SAs, or delete expired SAs.

Protocol/transform handling:
- `sa_add_transform()`: registers the selected transform into a protocol entry. Responders allocate a new `struct proto`; initiators validate a responder-selected transform against proposals previously sent.
- `sa_validate_proto_xf()` and `sa_validate_xf_attrs()`: compare transform IDs and attributes between offered and selected proposals.
- `proto_free()`: releases SPIs, DOI protocol data, transform-attribute copies, and invokes DOI SPI deletion hooks.

Reporting:
- `sa_dump()`, `sa_report()`: debug/report-channel summaries.
- `sa_report_all()` and helpers print user-oriented SA status, protocol transforms, algorithms, SPIs, lifetimes, cookies, and phase information.

Other operations:
- `sa_teardown_all()`: tears down phase 2 SAs during shutdown.
- `sa_reinit()`: on configured HUP behavior, soft-expires active phase 2 SAs without active exchanges.
- `sa_flag()`: maps textual SA flags such as `active-only`, `__ondemand`, and `ikecfg`.
- `sa_mark_replaced()` / `sa_replace()`: mark old SAs replaced, remove DPD timers, and re-enable DPD on replacement SAs.

Dependencies:
- `doi`, `exchange`, `message`, `timer`, `transport`, `cert`, `key`, `policy`, `ipsec`, `dpd`, and `connection`.
- Uses KeyNote session close via `kn_close()` when policy sessions are attached.

Risk notes:
- Reference counting and timer callbacks are tightly coupled; timers hold SA references and manually clear pointers before releasing.
- `sa_free()` removes active timers and adjusts refcounts before `sa_remove()`, so misuse can underflow/over-release if called on partially managed SAs.
- Proposal validation requires all returned attributes to be present and checked, which may reject peers with non-identical but semantically compatible attribute encoding.
