# sources/test-tools/stress-ng/core-personality.c

Purpose: build compatibility unit for Linux process personality support.

Important APIs/types: does not define functions; conditionally includes `<sys/personality.h>` when Linux and header support are detected.

Control flow: none beyond preprocessor selection.

State/persistence: no state and no runtime side effects.

Dependencies/integration: depends on `config.h` feature detection. It likely ensures the build environment can compile personality-related stressor support.

Risks: because it has no exported symbol, its utility depends on build-system expectations; unsupported systems should compile with the include omitted.

Test signals: build on Linux with and without personality header detection and confirm personality stressor runtime behavior elsewhere.
