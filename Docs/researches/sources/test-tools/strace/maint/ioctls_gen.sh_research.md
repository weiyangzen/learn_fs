# sources/test-tools/strace/maint/ioctls_gen.sh

Purpose: orchestrates ioctl table generation from Linux include directories, producing `ioctls_inc.h` and optionally `ioctls_arch.h`.

Important APIs/types/functions: include path canonicalization, temporary `ioctls_hex.h`/`ioctls_sym.h`, helper invocations `ioctls_hex.sh` and `ioctls_sym.sh`, KVM splitting into arch output, Android staging inclusion, sorting, and trap cleanup.

Control flow: validate one or two include directories, generate known hex ioctl entries from selected headers, generate symbolic ioctl entries using compile/DWARF pipeline, split KVM constants to arch output, append Android staging ioctls if present, sort unique into `ioctls_inc.h`, then repeat arch-specific generation when an arch include directory is supplied.

State and persistence behavior: writes generated headers in the current directory and temporary helper headers that are removed by cleanup. Logs counts to stderr.

Dependencies and integration points: core maintainer tool for updating strace's ioctl lookup tables. Depends on Linux UAPI tree layout and the symbolic/hex helper scripts.

Risks: writes output in current directory, so invocation location matters. Helper failures can produce partial headers. KVM reassignment relies on `linux/kvm.h` string matching.

Test signals: generated counts should be plausible, headers should sort/deduplicate, and resulting strace build/tests should decode known ioctl constants.
