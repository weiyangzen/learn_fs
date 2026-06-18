# sources/test-tools/fio/lib/getrusage.h

Purpose: declares the fallback `getrusage` signature for platforms where fio supplies it.

Important APIs/types: includes `sys/time.h` and `sys/resource.h`, then declares `getrusage(int, struct rusage *)`.

Control flow/state: no state; callers use the normal libc-style function signature regardless of whether the platform or fio fallback supplies the body.

Dependencies/integration: used by portability builds and resource-stat code.

Risks/test signals: duplicate declaration conflicts are possible if build configuration includes this while libc also exposes an incompatible prototype. Compile tests across supported OS configurations are the main signal.
