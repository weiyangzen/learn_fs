<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.h -->
# sources/security-integrity/selinux/mcstrans/src/mcscolor.h

## Purpose

Public internal header for mcstrans color lookup operations. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Declares `finish_context_colors()`, `init_colors()`, and `raw_color()`.

## Control Flow

No control flow; daemon initializes colors, serves raw color lookups, and finishes on shutdown/reload.

## State and Persistence Behavior

No storage is declared here; color state is static in `mcscolor.c`.

## Dependencies and Integration Points

Included by `mcstransd.c` and tied to `secolor.conf` parsing.

## Risks and Edge Cases

Risk is lifecycle mismatch between daemon reloads and color state cleanup.

## Test Signals

`mlscolor-test` and daemon color requests are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.h -->
