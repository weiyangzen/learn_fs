# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.c

This file bridges DNSSEC wire-format RRsets to cryptographic verification. It extracts DNSKEY/DS/RRSIG fields, validates signature metadata, canonicalizes RRsets, enforces downgrade-protection algorithm requirements, and calls `verify_canonrrset()`.

RRset and key access:
- Local helpers read RR counts, RRSIG counts, RRSIG keytags, RRSIG algorithms, and RDATA pointers.
- `dnskey_get_flags()`, `dnskey_get_algo()`, `dnskey_calc_keytag()`, `ds_get_keytag()`, `ds_get_key_algo()`, and `ds_get_digest_algo()` expose DNSKEY/DS metadata.
- `dnskey_algo_is_supported()`, `dnskey_size_is_supported()`, and `dnskeyset_size_is_supported()` enforce algorithm and optional RSA key-size policy.
- `ds_digest_match_dnskey()` computes a DS digest from DNSKEY owner name plus DNSKEY RDATA and compares it to the DS record.

Algorithm needs tracking:
- `struct algo_needs` tracks which signing algorithms still require successful validation.
- `algo_needs_init_dnskey_add()`, `algo_needs_init_ds()`, and `algo_needs_init_list()` initialize requirements.
- `algo_needs_set_secure()`, `algo_needs_set_bogus()`, `algo_needs_missing()`, and `algo_needs_reason()` implement downgrade-protection reporting.

Signature verification flow:
- `dnskeyset_verify_rrset()` verifies an RRset against a DNSKEY set, optionally requiring all signaled algorithms to validate.
- `dnskey_verify_rrset()` verifies an RRset against one specific DNSKEY.
- `dnskey_verify_rrset_sig()` verifies one RRset/RRSIG/DNSKEY combination after all metadata checks.
- `MAX_VALIDATE_RRSIGS` limits the number of RRSIG validation attempts.

Canonicalization:
- `canonical_compare_byfield()` and `canonical_compare()` sort RR RDATA in DNSSEC canonical order, lowercasing embedded domain names where required by RR type.
- `canonical_tree_compare()` and `canonical_sort()` build rbtree ordering and remove duplicates.
- `insert_can_owner()` handles wildcard-expanded owner names according to RRSIG label count.
- `canonicalize_rdata()` lowercases name fields for RR types requiring canonical name treatment.
- `rrset_canonical()` builds the exact signature input buffer: RRSIG covered fields plus sorted canonical RRs.
- `rrset_canonicalize_to_buffer()` canonicalizes an auth-zone RRset without an RRSIG context.
- `rrset_canonical_equal()` compares two RRsets after canonical sorting.

RRSIG checks:
- Validates signer name format, signer/key name match, covered type, algorithm, keytag, DNSKEY protocol, ZSK flag, revoked-key constraints, and label count.
- `check_dates()` verifies inception/expiration with RFC 1982 serial arithmetic and configurable clock skew.
- `adjust_ttl()` clamps verified RRset TTL to original RRSIG TTL and signature expiration.

Security behavior:
- Unsupported DNSKEY algorithms can produce insecure or indeterminate depending on context.
- Signature mismatch is bogus; missing matching key/signature is bogus with EDE reason.
- Too many signature validations is bogus.
- Authority-section NSEC owner names may be rewritten to canonical owner after wildcard handling to avoid synthesized NSEC misuse in denial proofs.

Research notes:
- This is the main correctness-sensitive canonicalization layer.
- It depends on `val_secalgo.c` only after all DNSSEC metadata and canonical buffer construction have succeeded.
- The code is defensive about malformed RRSIGs, short DNSKEYs, off-tree signers, wrong covered types, revoked keys, and label-count abuse.
