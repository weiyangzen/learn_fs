# sources/test-tools/fio/lib/getrusage.c

Purpose: compatibility shim for platforms lacking a working `getrusage`.

Important APIs/functions: `getrusage(int who, struct rusage *r_usage)` returns `-1` and sets `errno = EINVAL` in this fallback implementation.

Control flow/state: no state; every call fails deterministically.

Dependencies/integration: includes `errno.h` and `getrusage.h`. Build configuration selects this file only when fio needs the fallback.

Risks/test signals: consumers must tolerate failure and not assume resource accounting is available. Tests should verify graceful degradation in stats paths when `getrusage` returns an error.
