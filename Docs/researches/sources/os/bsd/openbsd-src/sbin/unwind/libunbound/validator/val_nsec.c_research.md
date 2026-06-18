# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.c

## Purpose
Implements NSEC denial-of-existence helper logic for the DNSSEC validator. It checks NSEC type bitmaps, validates NSEC rrsets before use, and determines whether NSEC records prove NODATA, NXDOMAIN, insecure delegation, wildcard use, or wildcard absence.

## Main Responsibilities
- Parses NSEC type bitmaps safely by window.
- Extracts the NSEC next owner name from rdata.
- Verifies NSEC rrset security status through cache status or signature validation.
- Checks DS-specific NODATA proofs at delegations.
- Checks NODATA proofs for exact names, empty non-terminals, wildcard NSEC records, and wildcard empty non-terminals.
- Checks name-error coverage using canonical ordering and wraparound handling.
- Determines closest encloser from an NSEC owner/next pair.
- Proves positive wildcard applicability and absence of wildcard records.

## Key Functions
- `nsecbitmap_has_type_rdata`: low-level NSEC type bitmap membership test.
- `nsec_has_type`: checks a type in the first NSEC RR's bitmap.
- `nsec_get_next`: returns the next owner name and validates its dname encoding.
- `val_nsec_proves_no_ds`: validates DS absence or insecure non-delegation semantics for DS replies.
- `nsec_verify_rrset`: verifies or refreshes an NSEC rrset's secure status.
- `val_nsec_prove_nodata_dsreply`: DS-reply-specific proof orchestration using authority-section NSECs.
- `nsec_proves_nodata`: general NODATA proof logic.
- `val_nsec_proves_name_error`: NXDOMAIN/name-error coverage check.
- `val_nsec_proves_insecuredelegation`: detects parent-side NSEC proving insecure delegation.
- `nsec_closest_encloser`: derives closest encloser from NSEC proof material.
- `val_nsec_proves_positive_wildcard`: proves qname nonexistence and correct wildcard use.
- `val_nsec_proves_no_wc`: proves no applicable wildcard exists.

## Control Flow
Higher-level validator code passes candidate NSEC rrsets and query info into these predicates. DS-specific logic first looks for exact qname NSEC and validates it; if absent, it scans authority NSECs for empty-nonterminal and closest-encloser/wildcard conditions. General proof routines combine canonical owner/next coverage, type bitmap absence, CNAME/delegation exclusions, and wildcard closest-encloser checks.

## Dependencies and Integration
Uses validator utilities, signature verification, rrset cache security status updates, reply lookup helpers, dname canonical comparison, packed rrset structures, and sldns type constants.

## Notable Constraints and Risks
- Functions generally inspect the first NSEC RR in an rrset for owner/bitmap proof data.
- DS handling has special parent/child-side checks involving SOA, NS, and DS bits.
- Several routines return simple boolean proof results, so callers must attach appropriate validation status/reason handling.
