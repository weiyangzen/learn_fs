# sources/security-integrity/selinux/libsemanage/src/seuser_internal.h

## Purpose
Provides private declarations for Unix-login-to-SELinux-user records.

## APIs and integration
Exports `SEMANAGE_SEUSER_RTABLE`, file database init/release functions, and `semanage_seuser_validate_local()`. It ties public `seuser_record`, local/policy APIs, database plumbing, and sepol policydb validation together.

## State and risks
No persistent state is defined here, but declarations couple file-backed local seuser records to policy-backed user validation. `semanage_seuser_validate_local()` requires a transaction-safe context because its implementation performs nested database lookups while iterating.
