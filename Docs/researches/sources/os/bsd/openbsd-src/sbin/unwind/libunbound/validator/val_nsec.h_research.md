# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.h

This header declares the validator’s NSEC denial-of-existence interface. It is part of libunbound’s DNSSEC validation layer inside OpenBSD `unwind`.

It exposes helpers for proving DS absence, checking NSEC type bitmaps, proving NODATA, NXDOMAIN/name errors, positive wildcard correctness, wildcard absence, closest-encloser derivation, and insecure delegation detection. The API works with `ub_packed_rrset_key`, `query_info`, `reply_info`, validator/module environments, and DNSSEC key entries.

Key contracts:
- `val_nsec_prove_nodata_dsreply()` validates NODATA responses to DS queries and can return secure absence, insecure non-delegation, bogus validation failure, or unchecked lack of proof.
- `nsecbitmap_has_type_rdata()` and `nsec_has_type()` provide type bitmap inspection.
- `nsec_proves_nodata()`, `val_nsec_proves_name_error()`, `val_nsec_proves_positive_wildcard()`, and `val_nsec_proves_no_wc()` encode the major NSEC proof forms.
- `nsec_closest_encloser()` returns closest-encloser data after name-error proof.
- `val_nsec_proves_insecuredelegation()` identifies unsigned delegation proofs.

Important dependencies:
- Uses packed RRset storage and LDNS RR type constants.
- Reason strings and EDE codes are threaded through validation failures.
- The header is consumed by NSEC3 code for bitmap handling and by validator denial logic.

Research notes:
- This is a pure declaration file with detailed proof semantics in comments.
- It establishes the NSEC counterpart to `val_nsec3.h`; NSEC3 implementation reuses `nsecbitmap_has_type_rdata()` for type bitmap interpretation.
