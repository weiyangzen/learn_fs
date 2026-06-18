## sources/security-integrity/audit-userspace/.github/workflows/ci.yml

Purpose: GitHub Actions CI matrix for audit-userspace.

It runs on pushes and pull requests to master, builds in Ubuntu and Fedora containers with gcc and clang, installs distro-specific dependencies, runs `autoreconf`, configures with Python3, Kerberos, libcap-ng, LDAP, z/OS remote, experimental plugins, and io_uring enabled, then runs `make -j` and `make check`. State is CI environment only. Dependencies are container packages and Actions checkout. Risks include `latest` distro drift, broad feature flags increasing dependency fragility, and no sanitizer/static-analysis lane. Test signal is the matrix build/test result.
