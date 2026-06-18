## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/Makefile.am

Purpose: build/install fragment for `audisp-af_unix`.

It builds the PIE plugin from `audisp-af_unix.c` and local queue, links libaudit/auplugin/cap-ng, installs `af_unix.conf` under audit plugins.d with mode 640, and installs manpage metadata. State is installed binary and config. Dependencies include libaudit, libauplugin, optional libcap-ng, and hardening flags. Risks include install path assumptions (`/sbin`) matching config defaults and config file mode/dir ownership outside Automake. Test signals are build, install DESTDIR, and plugin runtime socket tests.
