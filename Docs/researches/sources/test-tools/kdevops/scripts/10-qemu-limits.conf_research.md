# sources/test-tools/kdevops/scripts/10-qemu-limits.conf

Purpose: PAM limits configuration raising memlock limits for the `libvirt` group.

Important APIs/types/functions: two limits entries set hard and soft `memlock` to `20000000`.

Control flow: applied by PAM/session limit handling after installation.

State/persistence behavior: affects login/session resource limits for `libvirt` group members.

Dependencies/integration: supports VFIO/QEMU workloads needing locked memory.

Risks/test signals: unit is kilobytes on many systems; value may be insufficient for large passthrough workloads. Test signal is `ulimit -l` for libvirt sessions.
