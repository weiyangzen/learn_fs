<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2why -->
# sources/security-integrity/selinux/python/audit2allow/audit2why

## Purpose
Acts as the `audit2why` command entry point using the same Python source as `audit2allow`, switching default behavior based on `os.path.basename(sys.argv[0])`.

## Important APIs, Types, And Functions
The same `AuditToPolicy` class and methods are used as in `audit2allow`. The important distinction is option parsing: `--why` defaults to true when the basename is `audit2why`, so `__output()` routes to `__output_audit2why()`.

## Control Flow
The program parses audit input and policy options, initializes `selinux.audit2why`, parses messages into the audit parser, then walks AVC messages and prints diagnostic causes and suggested remediation for booleans, missing TE rules, constraints, missing role allows, and typebounds.

## State And Persistence
It is normally read-only, consuming logs or stdin and printing explanations. It initializes policy-analysis state through the audit2why binding and calls `audit2why.finish()`.

## Dependencies And Integration Points
Depends on the same sepolgen and libselinux Python bindings as `audit2allow`, with optional `sepolicy` descriptions for booleans.

## Risks And Edge Cases
Because it shares the file with `audit2allow`, installed symlink/name correctness is functional. Policy mismatches between logged denials and current/supplied policy can produce misleading "would be allowed" or dontaudit explanations.

## Test Signals
Verify the installed symlink invokes why mode by default, `-p test_dummy_policy -i test.log` succeeds, and known boolean/TE/constraint denial samples produce expected explanation categories.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2why -->
