# sources/test-tools/ior/src/parse_options.h

Purpose: public declaration for IOR command-line parsing.

Important APIs: `ParseCommandLine(int argc, char **argv, MPI_Comm com)` returns an `IOR_test_t *` linked list of configured tests.

Control flow and integration: callers pass process command-line arguments and an MPI communicator. The implementation initializes default IOR parameters, parses command-line and optional script inputs, resolves AIORI backend options, allocates per-test result storage, and returns the test list.

State and persistence: no state in the header. The returned linked list and nested allocations are owned by the caller or later IOR cleanup paths.

Risks: only the top-level parser is declared, so tests that need `DecodeDirective()` or `ReadConfigScript()` must include private declarations or test through `ParseCommandLine()`. The API returns a raw pointer with no ownership documentation in the header.

Test signals: compile inclusion from IOR main code, parser smoke tests with DUMMY backend, and script parsing tests through the public function.
