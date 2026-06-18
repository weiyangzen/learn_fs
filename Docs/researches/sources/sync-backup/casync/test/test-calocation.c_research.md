# sources/sync-backup/casync/test/test-calocation.c

Purpose: exercises location parsing, formatting, patching, advancing, merging, opening, and ID generation.

Important APIs/types/functions: main builds `CaLocation` objects from strings, checks fields and formatted output, advances offsets, merges adjacent locations, opens referenced data, and validates chunk ID behavior.

Control flow/state: uses reference-counted location objects and temporary/local paths as needed. Assertions provide the oracle.

Dependencies/integration: covers `calocation`, file-root, digest, and util code central to archive origin tracking.

Risks/test signals: location syntax is user-facing and remote-sensitive; this test is a key guard against parser/formatter drift.

Source research group: `subset-b-009122`.
