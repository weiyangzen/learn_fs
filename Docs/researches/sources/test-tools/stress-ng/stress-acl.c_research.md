# sources/test-tools/stress-ng/stress-acl.c

## Purpose
`stress-acl.c` implements the `acl` stressor, generating and applying many valid POSIX ACL combinations to files and directories and verifying round-trip correctness.

## Important APIs, Types, And Functions
`stress_acl_setup` builds valid ACL objects from combinations of user/group/other permissions and ACL tags. `stress_acl_exercise` sets ACLs with `acl_set_file`, reads them back with `acl_get_file`, compares with `acl_cmp` or a text fallback, records metrics, and increments bogo ops. Helpers include `stress_acl_delete_all`, `stress_acl_perms`, and `stress_acl_free`. `stress_acl_info` registers options including `--acl-rand`.

## Control Flow
The stressor mmaps arrays for ACL handles and tested flags, generates valid ACLs, optionally randomizes order, creates a temp directory and file, synchronizes start, then repeatedly deletes existing ACLs and exercises both access and default ACL types where supported. It reports how many unique ACLs were tested and sets harmonic-mean nanosecond metrics for set/get operations before cleanup.

## State And Persistence
Runtime state includes heap/libacl ACL objects and mmap-backed arrays. Temporary filesystem state is a directory and file with ACL metadata that is deleted at cleanup. No persistent ACLs should remain.

## Dependencies And Integration Points
It requires libacl, `acl/libacl.h`, `sys/acl.h`, and non-static builds. It depends on temp path helpers, mmap helpers, sync-start, stress-ng metrics, and option parsing. Without support it registers `stress_unimplemented`.

## Risks
ACL semantics vary by filesystem, mount options, and Cygwin behavior; the code conditionally omits default ACLs or redundant group entries for those cases. The fallback comparison via `acl_to_text` assumes stable canonical text output. Large ACL generation can consume memory, so mmap failure is handled as no-resource.

## Test Signals
Direct `--acl` and `--acl-rand` runs validate generation, set/get, and comparison. Debian and kernel coverage include ACL runs, and filesystems without ACL support should return skip/not-implemented rather than hard failure.
