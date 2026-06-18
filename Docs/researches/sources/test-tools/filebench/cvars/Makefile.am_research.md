<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/Makefile.am -->
# `sources/test-tools/filebench/cvars/Makefile.am`

Purpose: Automake recipe that builds Filebench custom-variable distribution plugins as libtool modules installed below `@libdir@/filebench`.

Important targets: `lib_LTLIBRARIES` lists `libcvar-erlang.la`, `libcvar-exponential.la`, `libcvar-lognormal.la`, `libcvar-normal.la`, `libcvar-triangular.la`, `libcvar-uniform.la`, `libcvar-weibull.la`, and `libcvar-gamma.la`. `common_cvar_files` expands to `mtwist/mtwist.c mtwist/randistrs.c cvar_tokens.c`.

Control flow: each plugin target compiles its distribution-specific source plus the shared tokenizer and Mersenne Twister/random distribution implementation, except gamma also links the common files but internally uses `drand48()` rather than the MT state.

State and persistence: build output is a set of `.la` libraries installed under the Filebench library directory. No runtime state is defined here.

Dependencies and integration: depends on Autotools substitutions from `configure.ac`, libtool, and the shared CVAR ABI declared in `cvar.h`. These modules are dynamically loaded by Filebench by symbol name.

Risks: shared files are compiled into every plugin, increasing duplicated code and making fixes require rebuilding all modules. `cvar-gamma.c` does not use the same RNG pathway as the other modules despite being built with `mtwist` sources.

Test signals: `make -C cvars` should produce every listed `.la`; install layout should place them in `libdir/filebench` so Filebench can locate CVAR modules.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/Makefile.am -->
