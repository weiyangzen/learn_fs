<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/version.inc.sh -->
# sources/security-integrity/keyutils/tests/version.inc.sh

## Purpose
Shell version-comparison library used by the keyutils tests to gate kernel, RHEL, and keyutils behavior.

## Important APIs, Types, And Functions
Defines `version_less_than`, internal `__version_less_than_dot`, `keyutils_older_than`, `keyutils_at_or_later_than`, `keyutils_newer_than`, `keyutils_at_or_older_than`, `kernel_older_than`, `kernel_at_or_later_than`, `rhel6_kernel_at_or_later_than`, and `rhel7_kernel_at_or_later_than`.

## Control Flow
`version_less_than` splits versions into base and release portions, gives `rc` releases pre-release ordering, and delegates dot-separated numeric/string component comparison to `__version_less_than_dot`. Public wrappers compare against `KEYUTILSVER`, `KERNELVER`, `OSDIST`, and `OSRELEASE`.

## State And Persistence Behavior
No state is persisted; it depends on global variables prepared by `prepare.inc.sh`.

## Dependencies And Integration Points
Used by many tests to handle historical kernel/keyutils differences in errno behavior, argument support, feature availability, and distro backports.

## Risks And Edge Cases
The comparison is shell/string based and can misorder unusual version components. It assumes release separators and `rcN` naming conventions.

## Test Signals
Signals are correct gating of version-sensitive tests such as timeout errno, search overlong descriptions, unlink-all support, and notification capability fallbacks.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/version.inc.sh -->
