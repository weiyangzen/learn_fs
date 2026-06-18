# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.timer

- Purpose: systemd finalization timer; it schedules the timeout finalizer near the 24-hour VM lifetime guard. The file is 10 lines/129 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.timer`.
- Important APIs/types/functions: systemd unit sections `Unit, Timer, Install` with directives Description=GCE finalization timer; OnBootSec=23h 45m; WantedBy=timers.target.
- Control flow: systemd evaluates ordering/conditions, then runs the configured unit action; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
