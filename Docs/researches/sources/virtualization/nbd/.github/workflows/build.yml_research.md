# File Research: sources/virtualization/nbd/.github/workflows/build.yml

This GitHub Actions workflow builds NBD on every push using `ubuntu-latest`.

It installs DocBook, GLib, GnuTLS, libnl-genl, Autoconf Archive, and `gcovr`; checks out the repository; runs `./autogen.sh`; configures with `--enable-syslog`; builds and runs `make check` with coverage flags; generates Cobertura XML and HTML coverage; submits coverage to Coveralls; and uploads `coverage.xml` plus `coverage.html` as an artifact.

The workflow is a CI coverage pipeline rather than a release workflow. Its dependency list mirrors major optional features in `configure.ac`: manpage generation, GLib, TLS, netlink, and Autotools bootstrap support.
