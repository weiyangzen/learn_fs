# sources/security-integrity/audit-userspace/lib/fieldtab.h

Purpose: Lookup input mapping audit rule field constants to command-line/textual field names.

Important entries: Includes process/user/group fields (`pid`, `uid`, `auid`, `loginuid`), subject/object SELinux fields, session, device/inode/exit/success, watch/path/dir/perm/filetype/fstype, interfield compare marker, syscall args `a0`-`a3`, `key`, `exe`, and `saddr_fam`.

Control flow: No runtime logic; generated into `fieldtabs.h` with lower-case string-to-int and int-to-string helpers and duplicate-int support. Duplicate `AUDIT_LOGINUID` maps both `auid` and `loginuid`.

State and persistence: Static mapping used by libaudit rule parser/display.

Dependencies and integration: Constants come from kernel audit headers. Used heavily by `audit_rule_fieldpair_data` and `audit_rule_interfield_comp_data`.

Risks: Text names are user-facing CLI syntax, so renaming breaks rule compatibility. Duplicate aliases must preserve preferred reverse mapping order.

Test signals: Parser tests for each field name, alias handling, and reverse display for duplicated fields.
