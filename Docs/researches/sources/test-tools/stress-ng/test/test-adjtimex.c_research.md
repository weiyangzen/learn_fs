# sources/test-tools/stress-ng/test/test-adjtimex.c

Purpose: compile probe for the `adjtimex()` time tuning call and `struct timex`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `adjtimex`; includes: `<sys/timex.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `adjtimex`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
