# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/journald.conf.d/99-gce-xfstests.conf

- Purpose: journald noise-control drop-in; it disables journal forwarding to console, wall, and kmsg on GCE test appliances. The file is 5 lines/73 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/journald.conf.d/99-gce-xfstests.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements Journal; key lines include ForwardToConsole=no, ForwardToWall=no, ForwardToKmsg=no.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
