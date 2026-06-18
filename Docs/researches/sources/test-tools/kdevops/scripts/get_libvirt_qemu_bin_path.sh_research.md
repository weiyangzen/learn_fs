<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirt_qemu_bin_path.sh -->
# sources/test-tools/kdevops/scripts/get_libvirt_qemu_bin_path.sh

Purpose: prints the expected QEMU system emulator binary path for the host architecture.

Important APIs and functions: no functions. It echoes `/usr/bin/qemu-system-` followed by `uname -m`.

Control flow: single echo command.

State and persistence: no state or writes; output depends on the runtime kernel architecture string.

Dependencies and integration: bash and `uname`. It likely feeds libvirt/Kconfig defaults for QEMU binary location.

Risks: not all distributions place QEMU binaries under `/usr/bin`, and some architecture names differ from QEMU binary suffixes. It does not verify the path exists or is executable. Test signals include asserting output for common architectures and adding an existence check in consumers or tests where a real host has QEMU installed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_libvirt_qemu_bin_path.sh -->
