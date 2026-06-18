<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.h -->
# sources/security-integrity/selinux/mcstrans/src/mls_level.h

## Purpose

Header for MLS level parse/format helpers shared by mcstrans translation and color code. The source was read completely for this report (10 lines).

## Important APIs, Types, and Functions

Declares `mls_compute_string_len()`, `mls_level_from_string()`, and `mls_level_to_string()` over `mls_level_t` from libsepol.

## Control Flow

No executable flow; consumers allocate/format/destroy MLS level data through the implementation and libsepol helpers.

## State and Persistence Behavior

No state is declared in the header.

## Dependencies and Integration Points

Depends on `sepol/policydb/mls_types.h` and pairs with `mls_level.c`.

## Risks and Edge Cases

Risk is ownership ambiguity for heap-returned strings/levels if callers do not follow implementation expectations.

## Test Signals

Compile coverage plus round-trip parse/format tests are the signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.h -->
