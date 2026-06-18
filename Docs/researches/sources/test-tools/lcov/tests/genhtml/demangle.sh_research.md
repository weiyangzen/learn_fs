<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/demangle.sh -->
# sources/test-tools/lcov/tests/genhtml/demangle.sh

- Purpose: Exercises `genhtml` C++ demangling modes with a synthetic trace containing plain and mangled function names.
- Important APIs/types/functions: Shell functions `die`, `cleanup`, `prepare`, and `run`; `prepare` writes a temporary info/source pair and `run` captures genhtml stdout/stderr.
- Control flow: Runs no-demangle, default `c++filt`, custom demangler, and custom demangler with parameters, then greps generated function HTML for expected transformed names.
- State and persistence behavior: Creates `out_demangle`, stdout/stderr logs, `demangle.info.tmp`, and `file.tmp`; cleanup removes core generated inputs.
- Dependencies and integration points: Depends on `$GENHTML`, optional `c++filt`, local `mycppfilt.sh`, Perl filtering, and genhtml function-view HTML naming.
- Risks: HTML class/name and environment-specific demangler output can vary; the script accepts either of two default conversions.
- Test signals: Passing signals are clean stderr, expected exit code, and generated function names in `${OUTDIR}/genhtml/file.tmp.func.html`.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/demangle.sh -->
