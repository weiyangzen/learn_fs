# sources/security-integrity/selinux/libsepol/src/user_internal.h

## Purpose
`user_internal.h` is the internal aggregation header for SELinux user record and collection APIs.

## APIs and Integration
It includes `<sepol/user_record.h>` and `<sepol/users.h>` behind `_SEPOL_USER_INTERNAL_H_`, defining no additional functions or types. `user_record.c` and `users.c` use it to share opaque user API declarations.

## Risks and Test Signals
The risk profile is minimal and mostly dependency-related. Build coverage of user record and policydb user management validates it.
