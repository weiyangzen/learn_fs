<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_relabel.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_compute_relabel.c

## Purpose

Computes the relabel/change SID for source and target contexts under a target class. The source was read completely for this report (67 lines).

## Important APIs, Types, and Functions

`main()` mirrors the member utility but calls `sepol_change_sid()` and prints the converted output context.

## Control Flow

Load policy, convert contexts/class, compute changed SID, convert to context, print, and clean up.

## State and Persistence Behavior

No persisted state; uses transient libsepol SID values and a heap context string.

## Dependencies and Integration Points

Depends on libsepol policy loading and service decision APIs.

## Risks and Edge Cases

Risks are equivalent to the member tool: sparse diagnostics and reliance on global policydb initialization.

## Test Signals

Known relabel transition fixtures provide the best smoke signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_relabel.c -->
