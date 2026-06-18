# sources/test-tools/strace/src/empty.h

Intentionally empty header used as a build-system placeholder or include target where generated or optional headers may be absent. It declares no APIs, types, macros, state, or control flow. Its only integration point is the preprocessor: including it must have no side effects. The risk is accidental population changing semantics for users that rely on a no-op include. Test signals are compilation of translation units that include it and repository checks that tolerate zero-byte headers.
