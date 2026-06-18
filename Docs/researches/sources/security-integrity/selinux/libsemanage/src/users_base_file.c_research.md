# sources/security-integrity/selinux/libsemanage/src/users_base_file.c

## Purpose
Parses and prints file-backed base SELinux user records.

## APIs and persistence
`user_base_print()` emits `user NAME roles { ... } [level L range R];`. `user_base_parse()` reads the same grammar, supports braced or unbraced role lists, optional MLS level/range, and semicolon termination. `user_base_file_dbase_init()` binds file storage to the base record table.

## Dependencies and risks
Uses `parse_utils`, ctype scanning, and base record setters. Roles and MLS strings cannot contain unescaped delimiter whitespace/semicolons. Parser mutates the input buffer while tokenizing, so ownership remains with parse infrastructure.
