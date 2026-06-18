# sources/security-integrity/selinux/sandbox/Makefile
# sources/security-integrity/selinux/sandbox/Makefile

Purpose: builds and installs SELinux sandbox tools.

Important APIs and control flow: defines install directories, compiler flags, libselinux/libcap-ng libraries, and `SEUNSHARE_OBJS`. `all` builds `sandbox`, `seunshare`, `sandboxX.sh`, `start`, and translations. `install` places `sandbox` in `bin`, installs manpages, installs `seunshare` setuid (`4755`) under `sbin`, installs helper scripts under the sandbox share directory, and installs `sandbox.conf`. `test` runs `test_sandbox.py -v`.

State and persistence: build outputs, installed setuid helper, config, scripts, translations, and manpages.

Dependencies and integration points: depends on Python, compiler, libselinux, libcap-ng, and PO Makefile.

Risks and test signals: setuid installation of `seunshare` is security-critical and makes compile warnings fatal by default. `make test` depends on SELinux enforcing mode and installed policy.
