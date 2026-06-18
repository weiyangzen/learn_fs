## sources/test-tools/syzkaller/syz-cluster/workflow/boot/Dockerfile

This Dockerfile builds the boot workflow action image. It supports `SMOKE_TEST=0` with Debian plus `qemu-system` and `openssh-client`, and `SMOKE_TEST=1` with a slim dependency-skipping setup. The final stage creates a `syzkaller` user, copies syzkaller binaries and `/bin/boot-action`, and sets the entrypoint.

Integration is with `boot/workflow-template.yaml`. Runtime assumptions include KVM/QEMU availability, syzkaller binaries under `/syzkaller/bin`, and action binary from the cluster builder. Risks include privileged runtime requirements handled in YAML, package variability, and smoke-test images not containing real VM dependencies.
