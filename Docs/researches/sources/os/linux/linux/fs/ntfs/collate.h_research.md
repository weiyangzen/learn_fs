# File Research: sources/os/linux/linux/fs/ntfs/collate.h

Declares NTFS collation support and validates supported collation rule IDs.

Exports:
- `ntfs_is_collation_rule_supported()` checks support for binary, NTOFS ULONG, NTOFS ULONGS, and file-name collation.
- `ntfs_collate()` compares two data items using a selected NTFS collation rule.

Core mechanics:
- The inline support check first rejects rules outside the implemented set, then verifies the numeric rule is within the standard NTFS supported ranges.
- Consumers can cheaply reject unsupported index collation before attempting comparisons.

Notable risks:
- The support check allows only the implemented rules despite recognizing standard numeric ranges, so any future rule requires both this header and `collate.c` dispatch changes.
