<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/mycppfilt.sh -->
# sources/test-tools/lcov/tests/genhtml/mycppfilt.sh

- Purpose: Dummy C++ demangler replacement used to verify custom `genhtml --demangle-cpp` command and parameter passing.
- Important APIs/types/functions: Executable filter: skips leading options, chooses a prefix from remaining args or `aaa`, and rewrites `FN`/`FNDA` records with Perl.
- Control flow: Reads lcov records from stdin and prefixes function-name fields before exiting 0.
- State and persistence behavior: Streams stdin/stdout only; no files are written.
- Dependencies and integration points: Depends on bash regex matching, Perl substitution, and genhtml custom demangler invocation.
- Risks: Only `FN`/`FNDA` formats with commas are transformed, which is intentional for the fixture.
- Test signals: Passing signal is generated HTML containing prefixed function names.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/mycppfilt.sh -->
