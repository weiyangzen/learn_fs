# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm.service

- Purpose: systemd LTM server unit; it starts /usr/local/lib/bin/ltm when present so a launched appliance becomes the long-term manager. The file is 16 lines/269 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=GCE LTM server; ConditionPathExists=/usr/local/lib/bin/ltm; After=network-online.target; Type=simple; WorkingDirectory=/usr/local/lib/bin; ExecStart=/usr/local/lib/bin/ltm; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/bin/ltm; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
