# sources/security-integrity/selinux/libsepol/include/sepol/policydb/expand.h

Purpose: Declares internal module expansion helpers that convert modular policy structures into expanded kernel-ready policydb data.

Important APIs and functions: `expand_module_avrules`, `expand_module`, type/role/MLS semantic conversion helpers, `expand_rule`, `expand_avtab`, and `expand_cond_av_list`.

Control flow: Expansion maps module-local types/bools/roles/users through provided maps, expands type/role sets into concrete ebitmaps, copies or expands neverallow rules, and optionally runs assertion/hierarchy checks.

State and persistence: Mutates or fills destination policydb avtabs, role/user/type structures, conditions, and MLS ranges. May expand base into itself only for AV rules under documented map constraints.

Dependencies and integration points: Depends on handles and conditionals; called by public `sepol_expand_module` and fuzzers.

Risks: Incorrect maps corrupt policy semantics. Expanding neverallow rules in-place can duplicate entries if the documented constraints are violated.

Test signals: Module expansion with attributes, conditionals, MLS users/ranges, neverallow checks, and base==out AV expansion validate it.
