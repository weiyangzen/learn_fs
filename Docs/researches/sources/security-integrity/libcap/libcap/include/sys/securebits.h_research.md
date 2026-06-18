## sources/security-integrity/libcap/libcap/include/sys/securebits.h

Purpose: public compatibility wrapper that exposes Linux securebits definitions through `<sys/securebits.h>`.

Important APIs/types: C++ extern guards, `__user` definition, and inclusion of `<linux/securebits.h>`.

Control flow: header guard then include-only behavior.

State/persistence: none.

Dependencies/integration: bundled or system `linux/securebits.h`; included by code using `SECBIT_*` constants.

Risks: wrapper correctness depends on include path resolving the intended UAPI header; minimal content means all semantic drift is in the UAPI copy.

Test signals: compile code using `SECBIT_NOROOT`, `SECBIT_NO_SETUID_FIXUP`, and related locks via installed headers.
