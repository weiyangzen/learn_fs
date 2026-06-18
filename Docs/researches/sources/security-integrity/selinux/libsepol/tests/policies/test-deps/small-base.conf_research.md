# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/small-base.conf

## Purpose
This is a compact dependency base that preserves the core SELinux class, MLS, type, role, boolean, user, SID, and filesystem context scaffolding used by dependency tests.

## Important APIs, Types, And Functions
It declares the common object classes and permissions, `s0:c0.c23` MLS data, attributes such as `domain`, `system`, `foo`, and `files`, ordinary types such as `system_t`, `sysadm_t`, `file_t`, and `fs_t`, roles `system_r`, `user_r`, and `sysadm_r`, optional `base_optional_*` types, and booleans used by modules.

## Control Flow
The file is loaded by helper routines as a base policy. Its optional block requiring `base_optional_1` and `base_optional_2` should enable because both types are declared before the block.

## State And Persistence Behavior
The parsed policydb includes symbol tables, scope information, a small MLS lattice, users, initial SID context, xattr filesystem use declarations, and a proc genfscon.

## Dependencies And Integration Points
It integrates with general module fixtures that need a valid base without the specialized positive/negative required-symbol split.

## Risks And Edge Cases
Despite the `small` name, it still encodes many baseline object classes. Removing rarely used classes can break module parsing if a fixture requires them indirectly.

## Test Signals
The main signal is that a minimal base can load, link modules, and support optional block enablement without the large reference policy.
