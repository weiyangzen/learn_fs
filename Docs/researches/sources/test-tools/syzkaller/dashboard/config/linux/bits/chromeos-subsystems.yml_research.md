# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-subsystems.yml

Purpose: enables ChromeOS-specific and device-relevant subsystems on full ChromeOS kernels beyond what prepareconfig enables.

Important keys: package list/configfs, ESD/Incremental FS conditionals, Virtio FS/WL, USB configfs gadget functions, BinderFS/devices, KVM/AMD/Intel virtualization, vsockets, virtio block/net/console/pci, and `VIRTUALIZATION`.

Control flow: declarative config fragment with branch guards like `[-chromeos-6.6]`, `[chromeos-5.10]`, and generic symbol enables.

State and persistence: generated `.config` and Binder device string.

Dependencies and integration points: ChromeOS kernel backports, USB gadget stack, Android Binder on ChromeOS, virtualization stack, and syzkaller manager tags.

Risks: ChromeOS branches diverge; guards for ESD/Incremental FS must track feature removal/addition. Enabling virtualization and many USB gadget functions broadens coverage but can introduce build/boot noise.

Test signals: full ChromeOS configs should include ChromeOS-specific filesystems, Binder, USB gadget, and virtio/KVM surfaces and still boot.
