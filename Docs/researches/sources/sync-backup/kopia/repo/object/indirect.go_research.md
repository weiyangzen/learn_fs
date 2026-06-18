# sources/sync-backup/kopia/repo/object/indirect.go

Purpose: defines entries for indirect object index streams used to represent large or concatenated objects.

Important APIs/types/functions: `IndirectObjectEntry` and `endOffset`.

Control flow: `endOffset` returns `Start + Length`. The comment shows the JSON shape stored in indirect stream metadata.

State/persistence behavior: entries are serialized into indirect object indexes, pointing byte ranges at underlying object/content IDs.

Dependencies/integration: consumed by object manager concatenation, index loading, and object readers.

Risks/test signals: offset/length correctness is critical for reads and concatenation. Coverage is mostly through object manager and reader tests outside this work item.
