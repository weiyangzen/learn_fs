# sources/sync-backup/borg/docs/quickstart_example.rst.inc

Purpose: quickstart include that walks a user through repository creation, repeated archive creation, listing, extraction, deletion, and compaction.

Important APIs and control flow: examples use `borg -r /path/to/repo repo-create --encryption=aes-ocb`, `create`, `repo-list`, `list aid:<prefix>`, `extract aid:<prefix>`, `delete aid:<prefix>`, and `compact -v`. It illustrates Borg 2's archive-series model where duplicate archive names are normal and archive IDs disambiguate.

State and persistence: creates an encrypted repository, stores two archives sharing a name, soft-deletes one archive, and then compacts to reclaim repository space.

Dependencies and integration points: depends on the general repository, archive-ID, logging, and compaction docs. It is included by higher-level quickstart pages.

Risks: hard-coded sample fingerprints and timestamps are illustrative only. Deleting by name is risky because names can match multiple archives; the include explicitly recommends dry-run/list first.

Test signals: doctest-like smoke can verify command names and option spelling; integration tests should confirm `repo-create`, duplicate-name archive creation, ID-prefix listing/extraction, delete, and compact still match the documented flow.
