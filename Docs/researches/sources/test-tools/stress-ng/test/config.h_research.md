# sources/test-tools/stress-ng/test/config.h

Purpose: central lightweight configuration header for stress-ng compile probes in this `test/` directory. It supplies fallback feature definitions so individual probes can compile in isolation while still matching stress-ng's autoconf-style expectations.

Important APIs/types/functions: preprocessor feature macros; includes: no external include beyond compiler defaults; defined macros include none.

Control flow: there is no runtime control flow. The file is included by small probe programs when they need common feature shims or neutral defaults before checking a platform API, compiler builtin, type, attribute, or instruction.

State and persistence behavior: no runtime state and no persistent state; it only affects preprocessing and compilation.

Dependencies and integration points: integrated with the stress-ng build feature-detection tests. Any macro here can change whether a probe compiles and therefore whether the main stress-ng build enables corresponding guarded code.

Risks and test signals: incorrect definitions can produce false-positive or false-negative feature detection. The signal is successful preprocessing/compilation of dependent tests rather than runtime behavior.
