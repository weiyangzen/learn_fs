# sources/user-network-fs/samba/source4/kdc/ad_claims.c

## Purpose

`ad_claims.c` constructs Active Directory claims for Kerberos PAC issuance. It decides whether claims are available at the current functional level, reads configured claim types, maps claim definitions to principal attributes, converts attribute values into NDR claim structures, and adds the constructed AuthenticationSilo claim when an enforced authentication silo applies.

## Important APIs, Types, and Functions

Public entry points are `ad_claims_are_issued()` and `get_claims_set_for_principal()`. Internal helpers include `add_attr_unique()` for sorted unique attribute search lists, `fill_claim_int64()`, `fill_claim_uint64()`, `fill_claim_uint64_oid_syntax()`, `fill_claim_boolean()`, `fill_claim_string()`, `fill_claim_string_sec_desc_syntax()`, and `fill_claim_entry()` for value conversion, `claim_applies_to_class()` for class scoping, `get_assigned_silo()` for constructed silo claims, `is_valid_claim_attribute_syntax()` for claim type validation, and `get_all_claims()` for the main DSDB query and assembly loop.

## Control Flow

`get_claims_set_for_principal()` exits unless the DC functional level is at least 2012, reads the principal's last structural class from `objectClass`, and calls `get_all_claims()`. `get_all_claims()` searches `CN=Claim Types,CN=Claims Configuration,CN=Services,<configDN>`, filters enabled claim definitions that apply to the principal class, validates source type and schema syntax, builds a deduplicated list of AD source attributes, and optionally handles the constructed `ad://ext/AuthenticationSilo` claim. If AD-sourced claims remain, it rereads the principal with only the needed attributes and fills `CLAIM_ENTRY` values into a `CLAIMS_SET`.

## State and Persistence Behavior

The file is read-only against DSDB. It allocates transient `CLAIMS_SET`, `CLAIMS_ARRAY`, and `CLAIM_ENTRY` structures under caller-provided talloc contexts and steals/moves successful results out of temporary contexts. It does not persist claims; they are computed for PAC construction from current directory configuration and principal attributes. Invalid individual attribute values are skipped with warnings where possible rather than aborting the whole claim set.

## Dependencies and Integration Points

It depends on DSDB schema lookup, LDB DN/value conversion, generated NDR claim and PAC types, binary search helpers, SDDL/security descriptor conversion, and `authn_policy_util` for authentication silo assignment. The output integrates with KDC PAC construction through `struct CLAIMS_SET`. Claim attribute syntax handling is coupled to AD schema OIDs such as integer, boolean, string, DN/OID, and security descriptor syntaxes.

## Risks and Edge Cases

Functional-level gates mean configured claims are silently absent below FL2012. Claim definitions with invalid source DNs, unsupported syntaxes, disabled state, missing names, or non-applicable classes are skipped. `add_attr_unique()` relies on the array being sized to the number of claim definitions plus a NULL terminator. Value conversion can drop malformed values, potentially issuing partial claims. Security descriptor syntax conversion fails the operation on NDR/SDDL errors.

## Test Signals

Useful tests cover no-claims behavior below FL2012, enabled/disabled claim types, class applicability, each claim value type and syntax, malformed source values being skipped or failed as designed, duplicate source attributes being searched once, constructed AuthenticationSilo claim issuance only for enforced assigned silos, and empty `claims_set_out` when no claim has values.
