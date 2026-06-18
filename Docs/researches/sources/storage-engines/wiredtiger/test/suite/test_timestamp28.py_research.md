<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp28.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp28.py

Purpose: Smoke test that commit timestamps are validated both when supplied at commit time and when set earlier with `timestamp_transaction`, including the earliest commit timestamp in a transaction.

Important APIs/types/functions: `test_timestamp28` uses `SimpleDataSet`, scenarios over `stable_timestamp` and `oldest_timestamp`, `conn.set_timestamp`, `session.timestamp_transaction('commit_timestamp=...')`, `commit_transaction`, and expected error patterns for each global timestamp type.

Control flow: The test sets stable or oldest to 30, then tries to commit at 20 and expects failure. It then sets a transaction commit timestamp 50, advances the global timestamp to 60 before commit, and expects commit failure. Finally, it sets commit timestamps 70 and 71 in one transaction, advances the global timestamp to 75, and confirms the earliest commit timestamp is used for validation even when commit is called with 80.

State and persistence behavior: The relevant state is the transaction's stored commit timestamp list/first commit timestamp and connection global timestamp. Table data is incidental.

Dependencies and integration points: Covers timestamp validation in both `timestamp_transaction` and `commit_transaction`, and integrates global oldest/stable constraints with transaction commit metadata.

Risks: If validation only checks the final commit argument, transactions could sneak older operations past oldest/stable constraints. Error strings differ by stable versus oldest path, so parser/message changes affect assertions.

Test signals: Three expected exceptions per scenario, each matched against the timestamp-specific error pattern.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp28.py -->
