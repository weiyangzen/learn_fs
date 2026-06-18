# sources/test-tools/crashmonkey/test/harness/TestTester.cpp

Purpose: test helper implementation for reaching into `Tester` internals during gtests. It provides a wrapper object and a method to replace the tester's device snapshot buffer.

Important APIs/types/functions: `TestTester::TestTester`, `set_tester_snapshot`, member `tester`, `Tester(false)`, `device_clone`, and `device_size`.

Control flow: constructor initializes `tester` with `false`. `set_tester_snapshot` deletes any existing `device_clone`, then assigns the caller-provided buffer pointer and size.

State/persistence behavior: mutates in-memory `Tester` snapshot ownership; the passed pointer becomes owned by `Tester`/helper and may be deleted later. Dependencies/integration: used by `TesterTest.cpp` to test snapshot save behavior.

Risks/test signals: ownership transfer is implicit and dangerous when passed stack storage; in the current test, a stack array is assigned, which can be unsafe if destructor later deletes it.
