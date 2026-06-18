## sources/test-tools/stress-ng/stress-vm-addr.c

Purpose: Implements `vm-addr`, stressing memory addressing patterns over mappings placed at many virtual addresses.

Important APIs/types/functions: `stress_vm_addr_info`, many `stress_vm_addr_*` pattern functions, `stress_vm_addr_all`, `stress_vm_addr_child`, and `stress_vm_addr`; options select method, mlock, and NUMA randomization.

Control flow: parent allocates a shared bit-error counter, optional NUMA masks, then runs an OOMable child. Child loops over power-of-two address hints and buffer sizes from 8 to 64 MiB, mmaps anonymous memory, optionally marks mergeable/randomizes NUMA/mlocks it, applies the selected address pattern, adds any readback mismatches to the shared counter, unmaps, and increments bogo.

State and persistence: only anonymous mappings and NUMA mask allocations; shared error counter survives child restarts until parent checks it.

Dependencies/integration: bit operations, cache flush in aggressive mode, madvise, NUMA helpers, OOM wrapper, target clones, SIGILL catch.

Risks: address-hint mmap may fail frequently; OOM avoidance adjusts size under low memory. Pattern correctness assumes power-of-two sizes and masks; detected bit errors are treated as failure.

Test signals: `VERIFY_ALWAYS`; any nonzero bit error count fails, and debug logs selected method.
