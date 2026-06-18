<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/chkcon.c -->
# sources/security-integrity/selinux/libsepol/utils/chkcon.c

## Purpose

Small command-line utility that loads a binary policy and checks whether one or more supplied SELinux contexts are valid under that policy. The source was read completely for this report (44 lines).

## Important APIs, Types, and Functions

`main()` expects a policy path followed by contexts, loads the policy with `sepol_set_policydb_from_file()`, then calls `sepol_check_context()` for each context and prints validity.

## Control Flow

Open policy, load libsepol global policydb, iterate contexts, report invalid entries, and return failure if any check fails.

## State and Persistence Behavior

State is limited to libsepol process-global loaded policydb state and the opened policy file; no output is persisted.

## Dependencies and Integration Points

Depends on `sepol/sepol.h` and `sepol/policydb/services.h`. It integrates as a developer diagnostic built by the libsepol utils Makefile.

## Risks and Edge Cases

Risks are global libsepol policy state reuse in long-running embedding and sparse CLI diagnostics for malformed policies.

## Test Signals

Manual smoke signal: valid contexts return success, invalid contexts print an error and produce non-zero exit status.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/chkcon.c -->
