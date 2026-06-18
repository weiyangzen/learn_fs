# sources/security-integrity/libcap/tests/uns_test.c

Purpose: privileged regression test for user namespace UID/GID map exploit behavior involving `CAP_SETFCAP`.

Important APIs/functions: lowers effective `CAP_SETFCAP`, changes uid through `cap_setuid()`, clones a child in `CLONE_NEWUSER`, writes crafted uid/gid maps under `/proc/<pid>/{uid,gid}_map`, and coordinates through pipes.

Control flow: if environment lacks effective `CAP_SYS_ADMIN`, exits 0 as not testable. Parent rotates uid 1 to 0, attempts map writes, and treats successful exploit launch as failure requiring kernel upgrade. Write or close failure on maps is the expected safe path.

State and dependencies: mutates capabilities, uid, namespaces, `/proc` map files, session state, and may exec `/bin/bash` in child.

Risks and test signals: highly privileged and environment-sensitive. It is run under sudo by `quicktest.sh` and tests kernel hardening rather than libcap logic alone.
