<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.c -->
# sources/security-integrity/selinux/mcstrans/src/mls_level.c

## Purpose

Utility code for converting libsepol `mls_level_t` values to and from textual MLS/MCS level strings such as `s0:c1,c2.c4`. The source was read completely for this report (175 lines).

## Important APIs, Types, and Functions

Exports `mls_compute_string_len()`, `mls_level_from_string()`, and `mls_level_to_string()`. It uses ebitmap iteration and libsepol MLS helpers to parse sensitivities and category ranges and to emit compact category ranges.

## Control Flow

Parsing turns text into a heap `mls_level_t`; formatting computes buffer length, emits sensitivity and category runs, and returns a heap string.

## State and Persistence Behavior

The caller owns returned `mls_level_t` and strings. No static state is owned here.

## Dependencies and Integration Points

Depends on `sepol/policydb/mls_types.h` and libsepol ebitmap/MLS helpers. It is used by translation and color modules.

## Risks and Edge Cases

Risks are off-by-one category range formatting, allocation failure cleanup, and accepting/rejecting malformed MLS strings consistently with the main parser.

## Test Signals

Round-trip tests of single categories, ranges, empty categories, and high category numbers are key signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.c -->
