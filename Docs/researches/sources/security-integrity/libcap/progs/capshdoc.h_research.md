# sources/security-integrity/libcap/progs/capshdoc.h

Purpose: small include guard and external declarations for the generated `capshdoc.c` data.

Important APIs/types: declares `extern const char **explanations[];` and `extern const int capsh_doc_limit;`.

Control flow/state: no control flow or persistent state. The guard prevents accidental multiple inclusion under `CAPSHDOC`.

Dependencies and integration: included by both `capsh.c` and `capshdoc.c`; consumers use `capsh_doc_limit` to avoid indexing beyond generated capability documentation.

Risks and test signals: declaration/type mismatch with `capshdoc.c` would be caught by compilation. Semantic drift is checked by `mkcapshdoc.sh` via the Makefile.
