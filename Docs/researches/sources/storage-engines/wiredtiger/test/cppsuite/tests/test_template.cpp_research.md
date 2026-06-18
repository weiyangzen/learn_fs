# sources/storage-engines/wiredtiger/test/cppsuite/tests/test_template.cpp

Purpose: minimal cppsuite template showing how to define a new harness test and custom operation tracker. It intentionally overrides all major workload hooks with no-op logging so developers can copy and replace pieces when creating a real test.

Important APIs, types, and functions: `operation_tracker_template` derives from `operation_tracker` and overrides `set_tracking_cursor`, currently delegating to the base implementation. `test_template` derives from `test`, initializes the operation tracker with `OPERATION_TRACKER`, compression, and timestamp manager configuration, overrides `run`, `populate`, operation hooks (`background_compact_operation`, `checkpoint_operation`, `custom_operation`, `insert_operation`, `read_operation`, `remove_operation`, `update_operation`), and `validate`.

Control flow: constructing `test_template` initializes tracking. `run` delegates to `test::run`, so the standard harness lifecycle still executes. Every operation hook logs a warning and performs no database work; validation also logs only.

State and persistence behavior: no application data is created by the template itself. The only state is framework initialization and any base harness scaffolding invoked by `test::run`. The custom tracker would control tracking table contents if changed.

Dependencies and integration points: included and dispatched by `run.cpp` as `test_template`. It depends on cppsuite constants, logger, configuration, timestamp manager, and operation tracking APIs.

Risks: because it logs no-op warnings but still runs the base harness, using the template unchanged can produce a passing test that does not validate behavior. Any copied test must replace both workload and validation methods to become meaningful.

Test signals: useful only as a compile/lifecycle smoke test. Expected runtime output is a sequence of warnings stating that populate, operations, and validation did nothing.
