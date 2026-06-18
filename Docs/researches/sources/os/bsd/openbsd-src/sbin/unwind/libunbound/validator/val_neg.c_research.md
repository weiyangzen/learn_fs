# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.c

## Purpose
Implements aggressive negative caching for DNSSEC denial-of-existence records. It indexes secure NSEC/NSEC3 rrsets by zone and owner name, then synthesizes negative responses or DS insecurity proofs from cached denial material.

## Main Responsibilities
- Maintains a locked negative cache with a zone rbtree, per-zone data rbtree, global LRU list, memory accounting, and size limit.
- Inserts secure NSEC records from negative replies and secure NSEC/NSEC3 records from referrals.
- Creates parent-chain nodes for zones/data so closest-enclosing lookup is efficient.
- Evicts least-recently-used denial records to stay within `neg_cache_size`.
- Removes stale/conflicting cached denial entries covered by newly inserted NSEC spans.
- Retrieves NSEC/NSEC3 rrsets from the rrset cache and verifies security/TTL suitability before using them.
- Synthesizes NOERROR/NODATA, NXDOMAIN, wildcard-derived answers, and DS negative proofs.

## Key Functions
- `val_neg_create`, `neg_cache_delete`, `val_neg_get_mem`: lifecycle and memory accounting.
- `neg_delete_data`, `neg_delete_zone`, `neg_make_space`: eviction/removal mechanics.
- `neg_create_zone`, `neg_insert_data`: build zone/data chain entries and insert denial records.
- `val_neg_addreply`: caches secure NSEC records from replies with SOA or signer-derived zone.
- `val_neg_addreferral`: caches NSEC/NSEC3 records from referrals after bailiwick/signer checks.
- `grab_nsec`: fetches a suitable NSEC/NSEC3 rrset from rrset cache, optionally checking absence of a type bit.
- `neg_find_nsec`: finds the best cached NSEC denial for a qname.
- `neg_find_nsec3_ce`, `neg_nsec3_getnc`, `neg_nsec3_proof_ds`: NSEC3 closest-encloser/next-closer DS proof logic.
- `add_soa`: adds SOA authority data when producing external negative responses.
- `val_neg_getmsg`: central message synthesis entry point.
- `val_neg_adjust_size`: updates cache limit and evicts as needed.

## Control Flow
Insertion paths find or create the relevant zone, mark it in-use, add each suitable denial rrset as an in-use data node, update NSEC3 parameters when applicable, and wipe cached records made obsolete by the inserted denial span. Lookup first tries NSEC-based NODATA/name-error synthesis. If aggressive NSEC is disabled, only DS queries continue. For DS queries, NSEC3 proof logic may create a response from closest-encloser and opt-out/next-closer records.

## Dependencies and Integration
Uses `val_nsec`, `val_nsec3`, `val_utils`, rrset cache, DNS message construction helpers, Unbound config, dname canonical ordering, and locks/rbtrees. The cache stores only indexes; actual rrset payloads are retrieved from the rrset cache.

## Notable Constraints and Risks
- The cache indexes denial records but depends on rrset cache retention; indexed records can become unusable if corresponding rrsets expire or are evicted.
- NSEC3 aggressive use is restricted mainly to DS proof handling.
- Large NSEC3 salts above `MAX_SALT_LENGTH` are declined for caching to avoid expensive hash work.
- `val_neg_getmsg` respects `cfg->aggressive_nsec` except for DS queries, which still use negative-cache proof paths.
