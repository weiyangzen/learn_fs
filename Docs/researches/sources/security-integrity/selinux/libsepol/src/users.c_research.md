# sources/security-integrity/selinux/libsepol/src/users.c

## Purpose
`users.c` translates high-level `sepol_user_t` records to and from `policydb_t` user datums and implements user query/modify/count/iterate APIs.

## Important APIs and Control Flow
`user_to_record()` converts a user datum by index into a public record, including role names and MLS strings. `sepol_user_modify()` unpacks the key and roles, finds or creates a `user_datum_t`, resets existing datums while preserving numeric value, validates role names, expands dominated roles, parses MLS default/range strings when MLS is enabled, rejects MLS strings when disabled, and for new users grows reverse lookup arrays and inserts the symbol.

## State, Persistence, and Integration
The file mutates `policydb->p_users`, `user_val_to_struct`, `p_user_val_to_name`, role bitmaps, MLS ranges, and caches. Data is persisted later by `write.c`. It depends on hashtab, role expansion, MLS parsing/formatting, and user record APIs.

## Risks and Test Signals
Error diagnostics can use a null `name` for existing-user failures. Partial new-user array growth must stay consistent on failure. Existing-user role cache behavior should be watched. Tests should cover new/modified users, undefined roles, MLS required/rejected fields, reverse lookup updates, query conversion, and iteration callback behavior.
