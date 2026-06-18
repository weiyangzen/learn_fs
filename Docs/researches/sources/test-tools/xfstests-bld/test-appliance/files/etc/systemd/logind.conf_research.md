# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/logind.conf

- Purpose: systemd logind appliance policy; it sets login/power-key/session behavior so VM shutdown and console handling suit automated tests. The file is 35 lines/963 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/logind.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements Login; key lines include HandlePowerKey=ignore.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
