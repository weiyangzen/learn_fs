# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/6

Purpose: OpenBSD pool double-free fixture with an explicit expected `REPORT:` subsection. Expected title is `pool: double put: lockfpl`.

Important parser APIs and patterns: handled by `panic: pool_do_put: ([^:]+): double pool_put`, formatted as `pool: double put: %[1]v`. The test also validates report-body extraction against the `REPORT:` block embedded in the fixture.

Control flow: the raw crash starts at `login: panic: pool_do_put: lockfpl: double pool_put`, stops at `db_enter`, and traces through `pool_do_put`, `pool_put`, `lf_advlock`, `VOP_ADVLOCK`, `closef`, `fdfree`, `exit1`, `sys_exit`, syscall, and `Xsyscall`. The `REPORT:` section records the expected normalized report text beginning at the login-prefixed panic.

State and persistence: static fixture containing lockf pool state, stack, and registers. CR-prefixed lines model OpenBSD console behavior.

Dependencies and integration: tests title extraction, report boundary normalization, and CR/LF cleanup in the OpenBSD reporter.

Risks: losing the `login:` prefix or mishandling CR characters can make expected report comparisons fail. Double-put and freelist-modified titles must remain distinct.

Test signals: exact title `pool: double put: lockfpl`; expected report starts with `login: panic: pool_do_put...`.
