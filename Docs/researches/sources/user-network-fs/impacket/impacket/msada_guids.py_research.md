# sources/user-network-fs/impacket/impacket/msada_guids.py

## Purpose
`msada_guids.py` is a static Active Directory GUID name catalog. It maps schema object GUIDs and extended-right GUIDs to human-readable names so tools can render security descriptors, ACE object types, validated writes, schema attributes/classes, and control-access rights meaningfully instead of showing raw GUID strings.

## Important APIs, Types, and Functions
The file exports two dictionaries and no functions or classes. `SCHEMA_OBJECTS` contains 1,769 lowercase GUID string keys mapped to Active Directory schema object names. Its values span core classes and attributes (`User`, `Computer`, `Group`, `Object-Guid`, `Object-Sid`), service families (FRS/DFSR, DHCP, DNS, MSMQ, MSSQL, WMI), certificate/PKI fields, terminal services fields, POSIX/NIS additions, and modern AD claims/device/authentication policy objects. `EXTENDED_RIGHTS` contains 80 lowercase GUID string keys mapped to control-access or validated-write names, including password changes, replication rights, certificate enrollment, `Send-As`, `Receive-As`, validated DNS host name, validated SPN, and other domain/security operations.

The dictionaries are plain module-level constants. The primary in-tree consumer is `examples/dacledit.py`, which imports both dictionaries, merges them into `OBJECT_TYPES_GUID`, and uses the merged mapping to label ACL object type GUIDs while editing or displaying Active Directory DACLs.

## Control Flow
There is no runtime control flow beyond Python module import and dictionary construction. Importing the module allocates both dictionaries. Consumers perform normal dictionary lookups or merge the dictionaries into their own mapping. Since `dacledit.py` calls `OBJECT_TYPES_GUID.update(SCHEMA_OBJECTS)` and then `OBJECT_TYPES_GUID.update(EXTENDED_RIGHTS)`, any duplicate GUIDs between the two maps are intentionally resolved in favor of the extended-right name for that consumer.

## State and Persistence Behavior
The module has no mutable state management, I/O, network access, or persistence. The exported dictionaries are mutable Python dictionaries, so an importing caller can accidentally modify global process state unless it copies them first. There is no generated-data timestamp or schema version metadata embedded beyond the header comments and source references.

## Dependencies and Integration Points
The file has no imports. It is populated from Microsoft MS-ADA schema references and a cleaned external SDDL parser data source noted in the header. Its main integration point is Active Directory security tooling that needs to map binary/string GUIDs to display names after converting LDAP security descriptor values. In this repository, `dacledit.py` is the visible direct integration; other tools could import these constants without side effects.

## Risks and Edge Cases
The main risk is data freshness and completeness. Active Directory schema extensions evolve across Windows releases and environments, and forest-specific custom schema GUIDs will not be present. The header explicitly notes that entries may be missing. The keys are lowercase hyphenated GUID strings; callers that use uppercase GUIDs, binary little-endian GUID forms, braces, or non-canonical formatting must normalize before lookup.

Because `SCHEMA_OBJECTS` and `EXTENDED_RIGHTS` can contain overlapping GUIDs, merge order matters. For example, a GUID may be meaningful both as a schema object and as a validated right label depending on context; a flat merged map can hide that distinction. The file provides no reverse mapping, collision detection, validation against duplicate values, or lookup helper that communicates unknown GUIDs cleanly.

## Test Signals
Tests should verify import succeeds with no dependencies and the dictionaries remain non-empty at expected scales (`SCHEMA_OBJECTS` around 1,769 entries and `EXTENDED_RIGHTS` around 80 entries). Spot checks should cover high-value rights such as `DS-Replication-Get-Changes`, `DS-Replication-Get-Changes-All`, `User-Force-Change-Password`, `Validated-SPN`, and `Send-As`, plus common schema objects such as `User`, `Computer`, `Group`, `Object-Guid`, and `User-Principal-Name`. Consumer tests for `dacledit.py` should cover GUID normalization, unknown GUID fallback, and duplicate-key merge behavior between schema objects and extended rights.
