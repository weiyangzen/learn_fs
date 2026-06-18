<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool.c -->
# sources/security-integrity/selinux/policycoreutils/setsebool/setsebool.c

## Purpose
Changes SELinux policy booleans either temporarily in the active policy or persistently through the semanage store.

## Important APIs, Types, And Functions
Important functions are `usage()`, `main()`, `selinux_set_boolean_list()`, `semanage_set_boolean_list()`, and `setbool()`. It uses `SELboolean`, `security_set_boolean_list`, semanage handle/transaction APIs, local boolean records and keys, active boolean update APIs, syslog, and passwd lookup.

## Control Flow
`main()` parses `-P` permanent, `-N` no reload, and `-V` verbose. It supports legacy `boolean value` syntax by synthesizing `boolean=value`, or multi-assignment syntax. `setbool()` parses each assignment, validates true/false/on/off/1/0 values, builds a `SELboolean` array, calls either active libselinux update or persistent semanage update, then logs each change to syslog.

## State And Persistence
Temporary mode mutates active kernel boolean state. Permanent mode opens the managed policy store, modifies local booleans, optionally sets active values if SELinux is enabled, and commits with optional reload suppression. Syslog records the caller.

## Dependencies And Integration Points
It bridges `setsebool` CLI syntax, active policy booleans, semanage persistent policy, and audit/operations logging through syslog.

## Risks And Edge Cases
`setbool()` temporarily overwrites `=` in argv strings and restores it during parsing, but not in the later syslog loop. Permanent mode requires managed policy and sufficient privilege. `-N` only affects semanage commits.

## Test Signals
Test both syntaxes, batches with mixed valid/invalid values, temporary failure for nonexistent booleans, permanent commits, no-reload, verbose semanage messages, non-root errors, and syslog names for uid without passwd entry.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool.c -->
