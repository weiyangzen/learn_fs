# sources/test-tools/strace/bundled/linux/include/uapi/linux/kexec.h

Purpose: defines userspace constants and segment layout for `kexec_load` and `kexec_file_load`, which load a replacement kernel or crash kernel.

Important APIs/types/functions: flags include `KEXEC_ON_CRASH`, `KEXEC_PRESERVE_CONTEXT`, `KEXEC_UPDATE_ELFCOREHDR`, `KEXEC_CRASH_HOTPLUG_SUPPORT`, file-load flags such as `KEXEC_FILE_UNLOAD`, `KEXEC_FILE_ON_CRASH`, `KEXEC_FILE_NO_INITRAMFS`, `KEXEC_FILE_NO_CMA`, `KEXEC_FILE_FORCE_DTB`, architecture encodings, `KEXEC_SEGMENT_MAX`, and `struct kexec_segment`.

Control flow: userspace passes an array of up to 16 segments for classic load, or kernel/initrd fds and flags for file load. Reboot into the loaded image occurs through a separate reboot path, not this header.

State/persistence behavior: load operations install or unload kernel crash/next-boot image state in the running kernel. The header warns that filesystem sync/unmount is not performed by kexec itself.

Dependencies/integration: depends on Linux types and architecture ELF numbering. Integrates with crash dump tooling, boot loaders, secure boot policy, and memory hotplug support.

Risks and test signals: risks include architecture mask decoding, pointer-size differences in `kexec_segment`, and privileged destructive semantics. Tests should decode flags, architecture values, segment arrays, unload mode, and no-initramfs/file-debug flags.
