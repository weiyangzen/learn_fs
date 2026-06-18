# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize-wait.service

- Purpose: systemd unit for finalization wait marker; it starts a wait loop that keeps finalization coordination visible until shutdown or cleanup clears it. The file is 14 lines/228 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize-wait.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=GCE finalization waiter job; After=local-fs.target; Wants=local-fs.target; Type=oneshot; ExecStart=/usr/local/lib/gce-finalize-wait; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/gce-finalize-wait; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
