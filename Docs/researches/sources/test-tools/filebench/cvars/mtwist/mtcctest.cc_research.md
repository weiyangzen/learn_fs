<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtcctest.cc -->
# `sources/test-tools/filebench/cvars/mtwist/mtcctest.cc`

Purpose: C++ test and benchmark harness for the `mt_prng` wrapper around the Mersenne Twister implementation.

Important APIs/functions: `main`, `report_timing`, C++ `mt_prng` methods `seed32`, stream save/restore operators, `lrand`, `llrand`, `drand`, `ldrand`, and `operator()`.

Control flow: optional argument sets timing loops in millions. The test seeds with `4357`, saves to `mtccsave`, reseeds with `1`, restores from file, deletes `mtccsave`, compares generated `lrand()` values against a long static `correct_values` vector, then benchmarks long, long long, fast double, long double, and call-operator generation while accumulating into volatile sinks.

State and persistence: creates temporary file `mtccsave` in the current directory to validate stream persistence. Otherwise state is held inside local `mt_prng rng`.

Dependencies and integration: includes `mtwist.h`, C++ streams/iomanip, `unistd.h`, `stdlib.h`, `sys/resource.h`, and `sys/time.h`. Validates the C++ class and stream operators defined in `mtwist.h`/`mtwist.c`.

Risks: default timing loop is 300 million iterations, expensive for routine CI. The test writes a fixed temporary filename in cwd and is not parallel-safe. It uses `unsigned long` expected values, which can vary in width but values are 32-bit.

Test signals: success prints `Validity test...passed.` and timing lines. Failures report expected/got value index and exit nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtcctest.cc -->
