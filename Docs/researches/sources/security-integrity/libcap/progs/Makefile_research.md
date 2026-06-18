# sources/security-integrity/libcap/progs/Makefile

Purpose: builds libcap command-line utilities: `getpcaps`, `getcap`, `setcap`, and `capsh`.

Important targets: `all`, `install`, `test`, `sudotest`, `clean`, `capshdoc.c.cf`, `capsh`, `tcapsh-static`, and `uns_test`. It supports dynamic, full static, and mostly-static libcap linkage through `DYNAMIC`, `LIBCSTATIC`, `LDFLAGS`, `LDFLAGS_SUFFIX`, and `DEPS`.

Control flow: ensures `../libcap/libcap.{a,so}` exists, compiles objects, links utilities, regenerates `capshdoc.c.cf` with `mkcapshdoc.sh` and diffs it against checked-in `capshdoc.c`, then builds static `tcapsh-static` for chroot/test use.

State and dependencies: consumes `Make.Rules`, libcap library artifacts, capsh documentation sources, and sudo for `sudotest`.

Risks and test signals: documentation generation drift fails the build. Static glibc limitations are called out. `sudotest` drives `quicktest.sh`, covering privileged capability behavior.
