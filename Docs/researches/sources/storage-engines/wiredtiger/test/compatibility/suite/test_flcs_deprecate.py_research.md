# sources/storage-engines/wiredtiger/test/compatibility/suite/test_flcs_deprecate.py

Purpose: Tests fixed-length column-store deprecation across branch upgrades.

Important APIs/types/functions: `test_flcs_deprecate` compares branch pairs against `mongodb-8.3`. `flcs_table_creation_unsupported` expects FLCS table creation to raise `ENOTSUP` on deprecated branches. `on_older_branch` creates a `key_format=r,value_format=8t` table and populates rows. `on_newer_branch` expects opening the old FLCS database to fail with a panic signal.

Control flow: pairs already at or past the deprecation version test creation failure; pairs crossing from pre-deprecation to deprecated run older-branch creation then newer-branch open failure.

State and persistence: the FLCS table is persisted in the test home by the older branch and reopened by the newer branch.

Dependencies/integration: uses the compatibility subprocess harness, `WTVersion`, Python `wiredtiger`, and `errno`.

Risks and test signals: assertions compare exception strings using substring-style membership against `wiredtiger_strerror`, so exact error formatting matters. The expected newer open failure is severe (`WT_PANIC`), making the test sensitive to future deprecation semantics.
