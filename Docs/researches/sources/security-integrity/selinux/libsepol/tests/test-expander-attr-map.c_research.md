<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.c

## Purpose

Validates expanded type-attribute membership for base, module, optional, and disabled optional declarations after `test-expander.c` has produced `base_expanded2`. The source was read completely for this report (138 lines).

## Important APIs, Types, and Functions

Exports `test_expander_attr_mapping()`. It defines expected type-name arrays for many `attr_check_*` attributes and calls `test_attr_types()` against `base_expanded2`; disabled optional symbols are checked with `hashtab_search()` and CUnit negated assertions.

## Control Flow

The test is linear: build expected arrays, assert membership for present attributes, assert zero-member attributes where optionals should not contribute, then verify disabled optional attributes and member types are absent from `p_types.table`.

## State and Persistence Behavior

No owned persistent state. It reads the external `policydb_t base_expanded2` initialized by the expander harness and uses stack arrays for expectations.

## Dependencies and Integration Points

Depends on local helper assertions, `sepol/policydb/policydb.h`, CUnit, and the policy fixture naming scheme under `policies/test-expander`.

## Risks and Edge Cases

The suite is sensitive to fixture symbol names and optional-enable semantics. A linker or expander change that leaves disabled optional symbols in the global type table will be caught here.

## Test Signals

The signal is exact attribute membership and absence coverage across base, module, optional, and disabled optional combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.c -->
