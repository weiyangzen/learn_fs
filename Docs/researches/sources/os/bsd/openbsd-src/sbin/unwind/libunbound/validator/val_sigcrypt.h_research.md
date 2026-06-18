# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.h

This header declares signature verification, DS/DNSKEY matching, DNSKEY metadata extraction, canonical RRset comparison, and algorithm downgrade-protection helpers.

Key structures:
- `ALGO_NEEDS_MAX` is 256, matching 8-bit DNSKEY algorithm identifiers.
- `struct algo_needs` stores per-algorithm states: not needed, needed, or bogus, plus outstanding count.

Algorithm tracking API:
- `algo_needs_init_dnskey_add()` adds DNSKEY algorithms to a requirement set.
- `algo_needs_init_list()` initializes from a signaled algorithm list.
- `algo_needs_init_ds()` initializes from DS records filtered by preferred DS digest algorithm.
- `algo_needs_set_secure()`, `algo_needs_set_bogus()`, `algo_needs_num_missing()`, `algo_needs_missing()`, and `algo_needs_reason()` support downgrade-resistant validation reporting.

DS/DNSKEY helpers:
- `ds_digest_match_dnskey()` checks DS digest against DNSKEY.
- `dnskey_calc_keytag()`, `ds_get_keytag()`, `dnskey_get_algo()`, `dnskey_get_flags()`, `ds_get_key_algo()`, and `ds_get_digest_algo()` parse key metadata.
- `dnskey_algo_is_supported()`, `dnskey_size_is_supported()`, `dnskeyset_size_is_supported()`, `ds_digest_algo_is_supported()`, and `ds_key_algo_is_supported()` expose support policy.

Signature verification API:
- `dnskeyset_verify_rrset()` verifies an RRset against a DNSKEY set.
- `dnskey_verify_rrset()` verifies against a single DNSKEY from a set.
- `dnskey_verify_rrset_sig()` verifies one signature with one DNSKEY and can reuse canonical sort/canonical buffer state.

Canonical RRset API:
- `canonical_tree_compare()` provides rbtree canonical ordering.
- `rrset_canonical_equal()` compares RRsets canonically.
- `rrset_canonicalize_to_buffer()` serializes an RRset into canonical wire form.

Research notes:
- This header is the primary interface between high-level validator logic and the lower crypto adapter.
- It includes EDE-aware failure reporting and packet section context because validation behavior differs for answer/authority processing.
