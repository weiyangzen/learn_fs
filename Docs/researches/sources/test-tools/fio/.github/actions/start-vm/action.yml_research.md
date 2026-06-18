# `sources/test-tools/fio/.github/actions/start-vm/action.yml`

Purpose: Composite GitHub Action that starts a QEMU/KVM guest VM and waits for SSH readiness.

Important APIs and inputs: Inputs include `qemu`, `image`, `ssh_fwd_port`, `options`, `ram`, and `host_key`. Steps install `wait-for-it`, configure KVM udev permissions, run QEMU in the background with host CPU, virtio disk, KVM, `q35`, user-mode networking and SSH port forwarding, then wait for the port and optionally add the host key.

Control flow: QEMU workflow calls this after creating the image and optional device backing files. Extra NVMe/null/other device options are appended directly to the QEMU command.

State and persistence: Leaves a background QEMU process running for subsequent workflow steps. Modifies runner udev rules and known_hosts when requested.

Dependencies and integration: Depends on QEMU binary availability, KVM support, root privileges for udev changes, and SSH server availability in the guest image.

Risks and test signals: The QEMU process is backgrounded without explicit PID tracking or teardown. `inputs.options` is command-line interpolated, so caller quoting must be correct. The wait timeout is short for slow boots. Tests should validate SSH command execution, device visibility in guest, and cleanup behavior after workflow completion.
