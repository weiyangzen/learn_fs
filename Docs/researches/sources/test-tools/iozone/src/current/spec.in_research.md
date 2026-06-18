# sources/test-tools/iozone/src/current/spec.in

Purpose: RPM spec template for packaging iozone version 3 release 414 into `/opt/iozone`.

Important APIs/types/functions: RPM sections include header metadata, `%description`, `%prep`, `%setup -n iozone3_414/src/current`, `%build`, `%install`, `%files`, and `%clean`. The build section selects make targets by `%ifarch` for x86, x86_64, ia64, ppc, ppc64, s390, s390x, and arm.

Control flow: during build, choose an architecture-specific iozone make target or fail with "No idea how to build for your arch...". During install, create `/opt/iozone/bin`, docs, and man directories under `$RPM_BUILD_ROOT`; copy `iozone`, `fileop`, `pit_server`, graph scripts/demos, PDFs/docs, and the man page; `%files` packages `/opt/` with root ownership and executable mode; `%clean` removes the build root.

State/persistence behavior: RPM build writes into `$RPM_BUILD_ROOT` and assumes source extraction under `$RPM_BUILD_DIR/iozone3_414`. It packages an entire `/opt` subtree rather than enumerating individual files.

Dependencies/integration: integrated with the iozone makefile `rpm` target and RPM tooling. It assumes tarball naming `%{name}%{version}_%{release}.tar`, docs outside `src/current`, and matching make targets for each supported architecture.

Risks/test signals: hard-coded version/release and paths must track source layout. `%files /opt/` is broad and may be undesirable for packaging hygiene. The `%ifarch %(arm)` syntax looks suspicious and needs rpm macro validation. Test signals are `rpmbuild -ba spec.in` on supported architectures and verification that expected binaries/docs/man pages appear in the RPM payload.
