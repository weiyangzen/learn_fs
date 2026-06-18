<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-object-links -->
# sources/sync-backup/bup/test/ext/test-validate-object-links

Purpose: tests low-level object-link validation for missing Git objects referenced from a saved tree. Important APIs are `bup validate-object-links`, `bup index`, `save --strip`, Git `ls-tree`, `rev-parse`, and manual object removal. Control flow saves a nested tree, validates successfully, finds the `.bupm` object under `src:a`, deletes or hides the referenced object, then expects validation failure and checks diagnostics for the missing object/reference path. State is the Git object database and branch `src`. Dependencies include Git object layout, btl helpers for tree entries, and WvTest. Risks are object traversal order and exact diagnostic content. Test signals are successful validation before corruption and exit code 1 after object removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-object-links -->
