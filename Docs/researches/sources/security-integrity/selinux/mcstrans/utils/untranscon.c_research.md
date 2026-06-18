<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/untranscon.c -->
# sources/security-integrity/selinux/mcstrans/utils/untranscon.c

## Purpose

Command-line mcstrans helper that converts a SELinux context in the translated context to raw context direction. The source was read completely for this report (28 lines).

## Important APIs, Types, and Functions

`main()` initializes translations, calls `untrans_context()` for the supplied context argument, prints the returned context, frees it, and finishes translation state.

## Control Flow

The utility is linear: validate CLI, initialize translation config, convert one context, print result, cleanup.

## State and Persistence Behavior

Runtime state is the translation engine globals initialized in `mcstrans.c` plus the returned heap context string.

## Dependencies and Integration Points

Depends on `mcstrans.h`, mcstrans source objects, libselinux/libsepol, and installed translation config.

## Risks and Edge Cases

Risks are poor behavior when MLS is disabled, config parse failures, and missing cleanup on early errors.

## Test Signals

Signals are example config round-trips and failure tests for malformed contexts/configuration.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/untranscon.c -->
