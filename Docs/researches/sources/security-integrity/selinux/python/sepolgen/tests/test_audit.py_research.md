# sources/security-integrity/selinux/python/sepolgen/tests/test_audit.py

## Purpose
This file tests audit log parsing and conversion of AVC records into access vectors. It uses embedded syslog/auditd AVC samples, AVC_PATH records, granted records, and ioctl extended-permission records.

## Important Tests And Exercised APIs
`TestAVCMessage` validates `AVCMessage` default fields, parsing of granted and denied records, SELinux source/target context fields, target class, access list, command name, denial flag, and `ioctlcmd` parsing including invalid or missing values.

`TestPathMessage` validates `AVC_PATH` extraction. `TestAuditParser` validates `parse_string()`, `parse_file()`, path post-processing across records with matching audit IDs, and xperm aggregation in `to_access()`. `TestGeneration` checks that denied records produce access vectors by default and granted records require `only_denials=False`.

## Control Flow
Tests instantiate parser/message classes, split embedded log strings, call `from_split_string()` or parser methods, and assert parsed fields. `parse_file()` opens a local `audit.txt` fixture from the current working directory. Xperm tests parse multiple AVCs with the same source/target/class and verify ioctl command ranges are coalesced into an `XpermSet`.

## State And Persistence
Most state lives inside message objects and `AuditParser` collections: `avc_msgs`, `compute_sid_msgs`, `invalid_msgs`, `policy_load_msgs`, and `path_msgs`. The file reads but does not write `audit.txt`.

## Dependencies And Integration Points
It depends on `sepolgen.audit` and `sepolgen.refpolicy`. Its output path integrates with `sepolgen.access.AccessVectorSet`, which is later used by policy generation. The test data covers both syslog-prefixed and audit daemon formats.

## Risks And Edge Cases
The parser is tested with a narrow set of historical log formats; TODO comments explicitly call for more message types and more log examples. Tests assume local fixture files and do not isolate the working directory. Invalid ioctl parsing is expected to silently yield `None`, so failures may be non-fatal by design.

## Test Signals
The file provides meaningful regression signals for AVC context parsing, granted/denied filtering, AVC_PATH correlation, and ioctl xperm range generation. It does not directly verify malformed record recovery beyond invalid ioctl values.
