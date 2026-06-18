# sources/test-tools/kdevops/scripts/10-qemu-hw-users.rules

Purpose: udev rule assigning VFIO devices to the `libvirt` group.

Important APIs/types/functions: single udev match `SUBSYSTEM=="vfio"` with `OWNER="root", GROUP="libvirt"`.

Control flow: evaluated by udev when VFIO device nodes appear.

State/persistence behavior: when installed under udev rules, affects ownership of VFIO device nodes.

Dependencies/integration: used for QEMU/libvirt hardware passthrough workflows.

Risks/test signals: assumes `libvirt` group exists and that group-level VFIO access is acceptable. Test signal is `ls -l /dev/vfio/*` group ownership after reload/trigger.
