# sources/user-network-fs/nfs-utils/support/junction/display.c

## Purpose
Maps FedFS status codes to readable text and prints status messages for libjunction callers.

## Important APIs, Types, and Functions
`nsdb_display_fedfsstatus()` and `nsdb_print_fedfsstatus()`.

## Control Flow
Display uses a switch over all known `FedFsStatus` values and returns a static string. Print reports success to stdout and errors to stderr.

## State and Persistence Behavior
No state or persistence beyond output streams.

## Dependencies and Integration Points
Depends on `junction.h` status enum and stdio. Used by junction command-line tools for diagnostics.

## Risks and Edge Cases
New enum values need switch updates. Output streams are fixed by status and not caller-configurable.

## Test Signals
Test every known status, unknown status fallback, stdout success, and stderr error output.
