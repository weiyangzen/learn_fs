# sources/test-tools/xfstests-bld/test-appliance/files/etc/phoronix-test-suite.xml

- Purpose: Phoronix Test Suite user config; it preseeds PTS preferences and result settings used when the appliance runs phoronix workloads. The file is 85 lines/3667 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/phoronix-test-suite.xml`.
- Important APIs/types/functions: declarative configuration with sections/elements XML or single-purpose config entries; key lines include <?xml version="1.0"?>, <?xml-stylesheet type="text/xsl" href="xsl/pts-user-config-viewer.xsl"?>.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
