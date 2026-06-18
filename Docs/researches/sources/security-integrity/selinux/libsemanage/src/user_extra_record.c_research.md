# sources/security-integrity/selinux/libsemanage/src/user_extra_record.c

## Purpose
Implements the extra, file-backed part of an SELinux user: name plus labeling prefix.

## APIs and state
Provides key extraction via shared user key creation, comparisons, getters/setters, create/clone/free, and `SEMANAGE_USER_EXTRA_RTABLE`. Records own heap strings for `name` and `prefix`.

## Dependencies and risks
Depends on `user_internal` and sepol key compatibility. Setters require non-NULL input. Clone logs source `name` on error, so malformed partially initialized records can affect diagnostics.
