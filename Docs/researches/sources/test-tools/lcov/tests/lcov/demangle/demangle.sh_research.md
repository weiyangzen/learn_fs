<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/demangle.sh -->
# sources/test-tools/lcov/tests/lcov/demangle/demangle.sh

- Purpose: Lcov demangling regression harness for C++ symbols, duplicate function records, simplification callbacks, and function/branch counts.
- Important APIs/types/functions: Procedural shell script using `demangle.cpp`, `simplify.pl`, lcov/geninfo/genhtml tools, compiler settings, and shared ignore options.
- Control flow: Compiles/runs the fixture, captures traces under demangle and simplify configurations, counts branches/functions, checks demangled names, and compares filtered outputs.
- State and persistence behavior: Creates binaries, `.gcno/.gcda`, `.info`, logs, and genhtml output directories; clean removes them.
- Dependencies and integration points: Depends on C++ compiler mangling, lcov demangle support, optional genhtml rendering, Perl simplification, grep/sed normalization.
- Risks: Compiler variance in inline constructor/destructor records and duplicate function entries can affect counts.
- Test signals: Passing signals are expected counts, demangled names, and replacement names from the simplify callback.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/demangle.sh -->
