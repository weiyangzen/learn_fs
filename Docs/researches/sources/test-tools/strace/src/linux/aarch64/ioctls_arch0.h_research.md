# sources/test-tools/strace/src/linux/aarch64/ioctls_arch0.h

Purpose: provides the `aarch64` generated architecture ioctl table, with 74 initializer rows from linux/kvm.h; examples include KVM_ARM_GET_REG_WRITABLE_MASKS, KVM_ARM_MTE_COPY_TAGS, KVM_ARM_PREFERRED_TARGET, KVM_ARM_SET_COUNTER_OFFSET, KVM_ARM_SET_DEVICE_ADDR, KVM_ARM_VCPU_FINALIZE.

Important APIs/types/functions: each row is `{'header, name, direction, number, size'}` data consumed by the common ioctl xlat machinery; observed direction flags include _IOC_NONE, _IOC_READ, _IOC_WRITE.

Control flow: no executable flow; entries are compiled into lookup arrays that let `ioctl(2)` decoding map command numbers back to symbolic names and argument direction/size.

State/persistence behavior: immutable compile-time metadata only; it neither reads traced memory nor persists runtime state.

Dependencies/integration: generated from Linux UAPI headers by `ioctls_gen.sh` and consumed by the strace ioctl decoder alongside generic include tables.

Risks/test signals: stale generated rows or wrong command sizes cause misleading ioctl names or argument decoding; test by comparing generated tables with current UAPI headers and tracing representative architecture-specific ioctl calls.

Source-read signal: reviewed complete local file (75 lines).
