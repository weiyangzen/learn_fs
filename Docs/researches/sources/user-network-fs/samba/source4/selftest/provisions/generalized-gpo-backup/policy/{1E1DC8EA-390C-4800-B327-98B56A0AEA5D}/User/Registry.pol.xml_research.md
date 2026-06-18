<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Registry.pol.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Registry.pol.xml

Purpose: XML-normalized user `Registry.pol` fixture.

Important APIs/types/functions: root `PolFile` with `signature=PReg`, `version=1`, and `num_entries=36`; entries for user certificate stores, trusted publisher safer settings, QoS policy, software restriction policy, and path rules with `REG_*` type names.

Control flow: static serialized representation of binary user registry policy.

State and persistence behavior: fixture only.

Dependencies and integration points: used by generalized GPO backup/restore tests for user registry policy parsing and binary/base64 value preservation.

Risks: includes a large certificate blob and many empty `REG_NONE` entries. Entry count and order may be used by round-trip tests.

Test signals: parser should read 36 entries and regenerate a valid user `Registry.pol`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Registry.pol.xml -->
