<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.cpp -->
# sources/test-tools/lcov/tests/genhtml/exception/exception.cpp

- Purpose: C/C++ fixture source for the lcov/genhtml tests in `sources/test-tools/lcov/tests/genhtml/exception`. It stresses exception branch capture/filtering.
- Important APIs/types/functions: Important declarations include: struct Throw {Throw () {throw std::exception();}};; struct NoThrow {NoThrow () {}};; static int a;; template<typename T>; bool test(); int main().
- Control flow: The nearby shell or Perl harness compiles, runs, diffs, or text-parses this file to generate specific coverage records and source-line edge cases.
- State and persistence behavior: Runtime state is local variables/stdout when compiled; persistent `.gcno/.gcda/.info` state is produced externally by the harness.
- Dependencies and integration points: Depends on compiler coverage instrumentation or lcov source parsing, plus the adjacent test driver.
- Risks: Line-number and syntax-shape sensitivity is high because coverage records, markers, and parser heuristics often refer to exact source layout.
- Test signals: Passing signals are expected trace records, filter decisions, branch/function counts, or generated HTML categories in the parent test.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/exception.cpp -->
