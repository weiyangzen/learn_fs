# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/stress.service

- Purpose: systemd stress workload unit; it starts the configured stress workload helper as a simple service. The file is 8 lines/111 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/stress.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service` with directives Description=Stress Workload; Type=simple; ExecStart=/usr/local/lib/start-stress.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/start-stress; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
