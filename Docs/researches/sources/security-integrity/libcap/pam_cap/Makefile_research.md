## sources/security-integrity/libcap/pam_cap/Makefile

Purpose: builds, installs, links, and tests the `pam_cap.so` PAM module and associated executable-shared-object behavior.

Important targets/variables: `all`, `install`, `execable.o`, `LIBCAP`, `pam_cap.so`, `pam_cap_linkopts`, `lazylink.so`, `test_pam_cap`, `testlink`, `incapable.conf`, `test`, `sudotest`, and `clean`.

Control flow: includes `Make.Rules`, forces PIC, builds libcap dependency, compiles executable-shared-object wrapper with loader text, determines whether `pam_cap.so` must link `-lpam` using `FORCELINKPAM` or `lazylink.so` probe, links the module with libcap, builds static and dynamic tests, creates an intentionally writable config for tests, runs module-as-executable checks, and privileged config cases under sudo.

State/persistence: creates module/test objects, `pam_cap_linkopts`, `lazylink.so`, `test_pam_cap`, `testlink`, and `incapable.conf`; installs into `$(LIBDIR)/security`.

Dependencies/integration: PAM headers/libs, libcap, executable shared-object support, loader text from libcap, sudo for privileged tests.

Risks: link behavior varies by distribution PAM packaging; `incapable.conf` is world-writable for test purposes and must not be installed; static test avoids `LDFLAGS` intentionally.

Test signals: `make -C pam_cap test`, direct `LD_LIBRARY_PATH=../libcap ./pam_cap.so --help`, and `make -C pam_cap sudotest` expected capability vectors.
