<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Registry.pol.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Registry.pol.xml

Purpose: XML-normalized machine `Registry.pol` fixture.

Important APIs/types/functions: root `PolFile` with `signature=PReg`, `version=1`, and `num_entries=76`; `Entry` nodes with registry key, value name, type/type_name, and one or more values. It covers certificate policy hives, QoS settings, software restriction policies, DNS client policy config, and binary certificate blobs.

Control flow: static serialized representation of binary machine registry policy entries.

State and persistence behavior: fixture only.

Dependencies and integration points: used by GPO backup/restore tests for `Registry.pol` parsing, type preservation, binary/base64 value handling, and machine-policy reconstruction.

Risks: large binary values and many empty `REG_NONE` entries can be accidentally normalized away. Entry count must match actual entries.

Test signals: parser should read 76 entries, preserve type distribution, and regenerate a valid `PReg` machine policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Registry.pol.xml -->
