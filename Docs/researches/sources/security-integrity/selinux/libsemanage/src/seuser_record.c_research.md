# sources/security-integrity/selinux/libsemanage/src/seuser_record.c

## Purpose
Implements `semanage_seuser_t` and key records for Unix login mappings.

## APIs and control flow
Records contain `name`, `sename`, and optional `mls_range`; keys contain `name`. The file provides key create/extract/free, compare/compare2/qsort comparator, getters/setters for all fields, create/clone/free, and the `SEMANAGE_SEUSER_RTABLE` database method table.

## State and dependencies
All fields are heap strings owned by the record. Setters replace old strings after successful `strdup()`. Clone deep-copies mandatory name and SELinux user plus optional MLS range.

## Risks and test signals
Setters do not accept NULL safely because they call `strdup()`. Cloning assumes source records are fully initialized except for optional MLS. Local seuser tests are indirect in this subset through validation and user deletion dependencies.
