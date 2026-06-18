## sources/sync-backup/bup/test/ext/test-compression

Purpose: verifies save compression levels affect repository size without changing saved contents.

Important control flow: saves `Documentation` once with `-0` and once with `-9`, compares latest archive listing to source listing each time, computes tar-based repo sizes, and asserts compression level 9 is smaller than level 0.

State and dependencies: repeatedly removes and recreates the temp Bup repo. Depends on `bup index`, `bup save`, `bup ls`, `tar`, and `wc`.

Risks covered: compression-level propagation into pack writing and preservation of directory contents under different compression settings.
