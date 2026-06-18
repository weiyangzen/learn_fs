<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/Audit/audit.csv.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/Audit/audit.csv.xml

Purpose: XML-normalized audit policy CSV fixture for machine policy backup.

Important APIs/types/functions: root `CsvFile`, header row, audit subcategories `Audit Credential Validation` and `Audit Kerberos Authentication Service`, GUIDs, inclusion settings `Success`/`Failure`, setting values `1`/`2`, and generalized `user_id` entity placeholders.

Control flow: static row data represents CSV policy content with generalized security principal references.

State and persistence behavior: fixture only; no runtime state.

Dependencies and integration points: used by generalized GPO backup tests for CSV parsing, user-ID token substitution, and restore fidelity.

Risks: XML contains custom Samba entity references that generic XML parsers need a resolver or placeholder handling for. CSV column ordering is part of the fixture contract.

Test signals: backup tooling should regenerate audit CSV rows and substitute principal tokens correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/Audit/audit.csv.xml -->
