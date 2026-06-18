# sources/sync-backup/borg/src/borg/testsuite/archiver/delete_cmd_test.py

Purpose: tests `borg delete` archive-selection behavior, multi-archive deletion, and protected archive handling.

Important APIs/types/functions: `test_delete_options`, `test_delete_multiple`, and `test_delete_ignore_protected` use `cmd`, `create_regular_file`, archive creation, `repo-list`, and `tag --add=@PROT`.

Control flow: `test_delete_options` creates several archives, deletes matching archives via shell match, last archive selection, and explicit `-a`, verifies one archive remains extractable, then deletes it and expects empty repo-list output. `test_delete_multiple` deletes two explicit archives and expects no archives left. Protected test tags one archive with `@PROT`, deletes explicit and pattern-matched archives, and verifies the protected archive remains while unprotected one is gone.

State and persistence behavior: repository archives and manifest entries are created, tagged, deleted, and listed. Archive data may remain pending compaction but manifest visibility changes.

Dependencies and integration points: covers delete command, archive matching/filtering, tag command, protected tag semantics, extraction as existence check, and local/remote/binary harness variants.

Risks: protected behavior is policy-sensitive; accidental changes could allow deleting protected backups. Output equality to empty string assumes no warnings/noise.

Test signals: validates archive selection deletes only intended archives and respects `@PROT`.
