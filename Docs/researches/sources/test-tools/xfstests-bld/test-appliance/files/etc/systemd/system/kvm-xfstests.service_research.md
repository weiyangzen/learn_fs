# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/kvm-xfstests.service

- Purpose: systemd KVM appliance boot unit; it runs /root/kvm-xfstests.boot once local filesystems, networking, and logging are ready. The file is 17 lines/340 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/kvm-xfstests.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=KVM-xfstests; After=local-fs.target network-online.target network.target; After=rsyslog.service; Wants=local-fs.target network-online.target network.target; Type=oneshot; ExecStart=/root/kvm-xfstests.boot; TimeoutStartSec=0; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /root/kvm-xfstests.boot; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
