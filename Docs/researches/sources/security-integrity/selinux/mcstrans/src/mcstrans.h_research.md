<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.h -->
# sources/security-integrity/selinux/mcstrans/src/mcstrans.h

## Purpose

Public internal header for mcstrans translation operations used by the daemon and helper utilities. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Declares `init_translations()`, `finish_context_translations()`, `trans_context()`, and `untrans_context()`, and includes `selinux/selinux.h` for SELinux types/config context.

## Control Flow

No control flow; callers use init before translation, call one of the conversion functions, and call finish during shutdown/reload.

## State and Persistence Behavior

No state is declared here; state lives in `mcstrans.c`.

## Dependencies and Integration Points

Connects `mcstrans.c` to `mcstransd`, `transcon`, and `untranscon`.

## Risks and Edge Cases

Risk is lifecycle misuse by callers, especially translation calls before successful initialization or after finish.

## Test Signals

Compile coverage and utility/daemon smoke tests validate the contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.h -->
