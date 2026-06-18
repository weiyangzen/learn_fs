<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp26.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp26.py

Purpose: Comprehensive tests for per-object timestamp usage assertions: write timestamp usage `never`/`ordered`, read timestamp assertions, `alter`, logged/in-memory behavior, and inconsistent per-key timestamp updates.

Important APIs/types/functions: Multiple classes cover targeted cases: `test_timestamp26_wtu_never`, `test_timestamp26_read_timestamp`, `test_timestamp26_alter`, `test_timestamp26_alter_inconsistent_update`, `test_timestamp26_inconsistent_update`, `test_timestamp26_log_ts`, and `test_timestamp26_in_memory_ts`. APIs include `session.create` with `write_timestamp_usage` and `assert=(read_timestamp=...)`, `session.alter`, `timestamp_transaction`, timestamped commits, `no_timestamp=true`, diagnostic/disagg skips, and `DisaggConfigMixin`.

Control flow: Tests verify timestamped commits are rejected for `write_timestamp_usage=never`, reads require or reject read timestamps according to `assert`, altering from `never` to `ordered` changes enforcement, decreasing per-key commit timestamps are rejected, once-timestamped keys must continue to use timestamps, and timestamp checks are ignored for logged/in-memory configurations unless object config overrides the environment.

State and persistence behavior: State is per-table configuration plus per-key timestamp usage history. Some tests move oldest to allow `alter`, and logged/in-memory scenarios validate environment-level timestamp ignoring rather than persistent history.

Dependencies and integration points: Integrates schema creation options, object alteration, transaction timestamp validation, diagnostic build behavior, disaggregated storage restrictions, logging, and in-memory configuration.

Risks: Several assertions are disabled in diagnostic builds because failures can dump transaction diagnostics or panic. Disaggregated storage has explicit incompatibilities for `write_timestamp_usage=never` and alter support.

Test signals: Expected `WiredTigerError` messages for disallowed timestamp use, decreasing timestamp order, missing timestamps, and read timestamp policy are the primary signals; smoke paths confirm valid orders still commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp26.py -->
