# sources/security-integrity/selinux/libsemanage/src/user_base_record.c

## Purpose
Adapts sepol user records as the base policy portion of libsemanage users.

## APIs and integration
Defines `semanage_user_base_t` as `sepol_user_t` and wraps sepol key extraction, comparison, name, MLS level/range, role management, create/clone/free. Exports `SEMANAGE_USER_BASE_RTABLE` for generic databases.

## State and risks
State ownership and validation are delegated to libsepol. The method table uses the public `semanage_user_key_free()` from the joined user layer, so key ownership must remain compatible with sepol keys.
