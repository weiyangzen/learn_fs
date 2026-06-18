<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archives_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archives_test.py

Purpose: unit tests for the `Archives` manifest/archive-index implementation and its `ArchivesInterface` contract.

Important APIs/types: `Archives`, `ArchiveInfo`, `ArchivesInterface`, `Repository`, `ItemInfo`, `StoreObjectNotFound`, `CommandError`, `Error`, `_id`, `_archives`, `_archive_meta`, `_archiveinfo`, `_stub_info_tuples`, and `_stub_matching_info_tuples`.

Control flow: early tests check interface methods, ids/count/names/existence, deleted flags, and metadata loading. Metadata tests mock `repo.get`, `repo_objs.parse`, and `key.unpack_archive` for success, missing archive, tags, defaults, and bad versions. Mutation tests verify `create`, `delete_by_id`, `undelete_by_id`, and `nuke_by_id` call store APIs. Listing tests cover type checks, generator materialization regression, sorting, reverse, first/last, date filters, deleted flag propagation, match patterns (`name`, `user`, `host`, `tags`, `aid`), exact-one selection, and `list_considering` CLI argument delegation.

State and persistence: mostly mocked repository/store state; archive objects are represented by store names under `archives/<hex-id>` and metadata dictionaries unpacked from archive objects.

Dependencies/integration: depends on borgstore list/get/move/delete semantics, archive metadata schema version 2, timestamp parsing, match grammar, and date filter delegation. Risks include ambiguous archive-id prefixes, generator misuse, incorrect deleted flag propagation, and compatibility parameters such as ignored `overwrite`. Test signals are mock call assertions, returned `ArchiveInfo` values, raised errors, sorted lists, and exact matched sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archives_test.py -->
