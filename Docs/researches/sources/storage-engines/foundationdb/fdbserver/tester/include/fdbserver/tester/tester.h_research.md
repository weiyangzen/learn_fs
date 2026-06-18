# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/tester.h

Purpose: Public tester API header declaring the tester server, top-level test runner, mode enums, and custom shard config workload.

Important APIs/types/functions: `testerServerCore`, `test_location_t` (`TEST_HERE`, `TEST_ON_SERVERS`, `TEST_ON_TESTERS`), `test_type_t` (`FROM_FILE`, `CONSISTENCY_CHECK`, `UNIT_TESTS`, `CONSISTENCY_CHECK_URGENT`), `runTests`, and `customShardConfigWorkload`.

Control flow: Header only; the enums steer `runTests` in `test.cpp`, selecting file parsing, generated consistency check, unit tests, or repeating urgent consistency checker, and selecting local/server/tester execution locations.

State and persistence behavior: No state in the header. Function signatures expose cluster connection, locality, unit test parameters, and restart flag state.

Dependencies and integration points: Includes locality, `TesterInterface`, and `UnitTest`. It is the include used by fdbserver/tester consumers and by `CustomShardConfigWorkload.cpp`.

Risks: `runTests` uses many const-reference parameters with defaults; implementation explicitly copies them for C++20 coroutine safety. Callers must choose correct enum combinations for the intended topology.

Test signals: Compile/link coverage and top-level tester execution. Invalid modes are generally asserted in implementation.
