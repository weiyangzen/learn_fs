# sources/security-integrity/libcap/tests/weaver.h

Purpose: public declarations for the weaver thread helper.

Important APIs/types: declares `pthread_t weaver_thread(void)`, `void weaver_setup(void)`, `int weaver_waitforit(int n)`, and `void weaver_terminate(void)`.

Control flow/state: none in the header; state lives in `weaver.c`.

Dependencies and integration: requires `pthread_t` to be visible to includers. Used by `weaver.c`; `b219174.c` obtains the same symbols dynamically with `dlsym()` instead of including the header.

Risks and test signals: type drift between declarations and implementation would break compilation. Runtime symbol drift is caught by `b219174.c`.
