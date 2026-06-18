# sources/test-tools/crashmonkey/test/harness/TestTester.h

Purpose: declares a small gtest helper around CrashMonkey `Tester`. It exposes a method for installing a synthetic device snapshot.

Important APIs/types/functions: class `TestTester`, constructor, `set_tester_snapshot(char *sn, size_t size)`, and public member `Tester tester`.

Control flow: implementation constructs `Tester(false)` and sets internal snapshot pointers. State/persistence behavior: in-memory only, but used to drive snapshot serialization in tests.

Dependencies/integration: includes `../../code/harness/Tester.h`. Risks/test signals: public `tester` breaks encapsulation intentionally for tests, and snapshot ownership conventions are not documented in the header.
