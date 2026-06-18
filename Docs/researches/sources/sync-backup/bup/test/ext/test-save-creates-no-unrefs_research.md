<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-creates-no-unrefs -->
# sources/sync-backup/bup/test/ext/test-save-creates-no-unrefs

Purpose: regression test that `bup save` does not leave unreferenced objects behind. Important APIs are `bup init`, `index`, `save`, and validation through Git/bup repository checks. Control flow creates a small source tree, saves it, and inspects the repository for unreferenced objects after the save. State is only the temporary bup repo and saved branch. Dependencies are WvTest and Git object reachability checks. Risks are pack writer flush ordering and transient refs during save causing later garbage or `fsck` noise. Test signals are successful save and absence of unreferenced object reports.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-creates-no-unrefs -->
