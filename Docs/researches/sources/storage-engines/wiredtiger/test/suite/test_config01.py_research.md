<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config01.py

Purpose: adapter test that reuses `test_base03` while substituting scenario-generated session creation configuration strings.

Important APIs and control flow: `test_config01` subclasses `test_base03.test_base03` and overrides only `config_string()` to return `self.session_create_scenario.configString()`. The inherited base test creates data sources, populates records, and validates base cursor/table behavior under many `session.create` configuration combinations.

State, persistence, and dependencies: persistence behavior is inherited from `test_base03`; this file's only state is the active scenario object. It depends on `test_base03` and whatever session-create scenarios that base class defines.

Integration points: connects the generic base table tests to the WiredTiger configuration scenario framework. It is an integration shim rather than an independent workload.

Risks and test signals: because behavior lives in the base class, failures may be misattributed to this small file. The signal is inherited base-test success across generated create configurations; risks are scenario object API drift or base-class renaming.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config01.py -->
