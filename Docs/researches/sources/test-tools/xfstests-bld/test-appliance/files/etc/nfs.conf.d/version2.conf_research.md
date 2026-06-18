# sources/test-tools/xfstests-bld/test-appliance/files/etc/nfs.conf.d/version2.conf

- Purpose: NFS daemon compatibility config; it enables UDP and NFSv2 service options for legacy xfstests coverage. The file is 4 lines/21 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/nfs.conf.d/version2.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements nfsd; key lines include udp=y, vers2=y.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
