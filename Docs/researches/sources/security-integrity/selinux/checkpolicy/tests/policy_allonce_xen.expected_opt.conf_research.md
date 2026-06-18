# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected_opt.conf

## Purpose

This file is the optimized expected output for the Xen target fixture under `--target xen -c 30 -E -S -O`.

## Important Semantics

The optimized file matches the non-optimized Xen expected output except that the redundant `BOOL1` conditional block is removed entirely. The unconditional `allow TYPE1 self:CLASS1 { PERM1 }` makes the false-branch conditional permission redundant, so no conditional remains.

## Control Flow And Integration

It is the oracle for the optimized Xen lane in `test_roundtrip.sh`, and the script verifies it is stable through repeated optimized compile/decompile.

## State And Persistence

The artifact persists Xen target state with optimizer-pruned conditionals. Xen-specific SIDs and hardware contexts must remain identical to the non-optimized expected file.

## Dependencies And Risks

The file is sensitive to optimizer block elimination and Xen target formatting. A regression can either keep redundant conditional output or accidentally remove nonredundant Xen target records.

## Test Signals

A passing diff confirms `-S -O` can eliminate a fully redundant conditional block while preserving Xen SID and device context output.
