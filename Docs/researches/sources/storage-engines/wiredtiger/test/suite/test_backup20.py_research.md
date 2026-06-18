# sources/storage-engines/wiredtiger/test/suite/test_backup20.py

Purpose: regression test for WT-7027, ensuring incremental backup `force_stop` works without a checkpoint and does not assert when the session uses snapshot isolation. It runs default, read-committed, read-uncommitted, and snapshot session configurations.

Important APIs are scenario `session_config`, table creation, opening an incremental primary backup cursor, opening a `force_stop=true` backup cursor, and explicit session/connection close. Control flow creates a table, opens/closes a primary incremental backup with granularity and `this_id=ID1`, then immediately opens/closes a force-stop cursor without taking a checkpoint. State behavior is incremental metadata setup and teardown without checkpoint persistence. Dependencies are `suite_subprocess` for assertion isolation. Risks are narrow: the test signals only absence of crash/assertion, not data content. Test signal is successful close under all isolation scenarios.
