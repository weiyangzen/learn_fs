# sources/test-tools/stress-ng/test/test-__restrict.c

Purpose: compile probe for the `__restrict` qualifier so stress-ng can use restricted pointer annotations in hot helper functions without breaking compilers that lack the spelling.

Important APIs/types/functions: `__restrict` pointer-qualified parameters or locals; observed symbols: `test`; includes: no external include beyond compiler defaults; macros: none.

Control flow: the probe calls a small function or expression using restricted pointers and exits. Runtime behavior is only present to force type checking.

State and persistence behavior: no persistent state; local variables or arrays exist only during the probe.

Dependencies and integration points: informs portability macros used across stress-ng for aliasing assumptions and optimization hints.

Risks and test signals: compilers may support standard `restrict` but not `__restrict`, or only in certain language modes. Clean compilation is the signal.
