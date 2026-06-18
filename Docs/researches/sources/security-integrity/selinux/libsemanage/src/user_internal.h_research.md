# sources/security-integrity/selinux/libsemanage/src/user_internal.h

## Purpose
Private user database interface for base policy users, extra prefix records, and joined public user records.

## APIs and integration
Declares record tables, file/policydb/join database init/release functions, base and extra record accessors, key unpacking, and join/split routines. It coordinates public users across `users_base_file`, `users_extra_file`, `users_base_policydb`, `users_join`, and local/policy CRUD files.

## State and risks
Defines the split-persistence model: policy user fields live in policydb/base files, while prefixes live in extra files. Callers must keep base and extra names synchronized through the join API.
