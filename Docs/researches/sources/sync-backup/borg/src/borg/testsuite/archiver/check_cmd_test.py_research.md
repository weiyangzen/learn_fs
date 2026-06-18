# sources/sync-backup/borg/src/borg/testsuite/archiver/check_cmd_test.py

Purpose: broad integration tests for `borg check`, archive selection filters, repository/archive repair, manifest rebuild, corrupted/missing objects, lost archive recovery, spoofed object defense, and data verification.

Important APIs/types/functions: `corrupt` flips a byte reliably. `check_cmd_setup` creates a repository and two archives with a patched small `ChunkBuffer.BUFFER_SIZE`. Tests use `open_archive`, `Repository`, `Manifest`, `ChunkBuffer`, `bin_to_hex`, `msgpack`, `fchunk`, and `create_src_archive`.

Control flow: usage tests assert repository-only and archives-only modes print the right phases and archive filters select expected archives. Date matching creates old and current timestamped archives and exercises oldest/newest/newer/older units. Corruption tests delete file chunks, archive item chunks, archive metadata, or manifest objects, run check with and without `--repair`, and assert repair restores checkability where possible. Spoofing tests write fake manifest/archive objects with wrong `ro_type` and ensure check rejects/removes them. `--find-lost-archives` verifies a missing archive directory entry can be rediscovered. Data verification corrupts file content objects and distinguishes normal archive checks from `--verify-data`.

State and persistence behavior: tests directly mutate repository object storage, manifest bytes, archive entries, and archive directory files. Repair commands rewrite manifest/archive metadata or delete bad chunks. Remote and binary parametrization is used where supported; some tests skip local-only direct object mutation.

Dependencies and integration points: integrates check command, repository object API, manifest load/write/rebuild, authenticated object type metadata, archive item iteration, chunk index behavior, archive filters, and repair paths.

Risks: direct repository mutation depends on storage layout and object IDs. Some expected archive names in date edge assertions look historical and may be weak. Repair semantics are security-sensitive: fake objects must not be accepted as manifests/archives merely because bytes parse.

Test signals: high-value regression coverage for repository integrity, repair safety, missing/corrupt object diagnostics, and `--verify-data` behavior across encrypted and unencrypted repositories.
