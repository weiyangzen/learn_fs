## sources/test-tools/stress-ng/stress-vforkmany.c

Purpose: Implements `vforkmany`, creating long chains of vforked processes and optional VM pressure.

Important APIs/types/functions: `stress_vforkmany_info`, `vforkmany_shared_t`, `vforkmany_wait`, and `stress_vforkmany`; options `vforkmany-vm` and `vforkmany-vm-bytes`; uses `fork`, `shim_vfork`, waitpid, alternate signal stack, KSM/madvise/mincore/OOM helpers.

Control flow: parent sets up alt signal stack and shared state, forks a worker, then sleeps until timeout and sets a termination flag. Worker can allocate/touch memory, then repeatedly vforks children; vfork children increment shared counters, measure startup latency, optionally madvise/touch memory, and continue spawning until stop. Parents wait for children to avoid zombies.

State and persistence: mmap-shared counters and termination flag; optional anonymous waste mappings; no files.

Dependencies/integration: careful static variables due to vfork shared address-space semantics, OOM adjustment, signal stack helpers, memory pressure utilities.

Risks: vfork semantics are fragile; stack/global misuse can corrupt parent state. Resource exhaustion and OOM are expected. Parent clears OOMable flag so the controller is less likely to be killed.

Test signals: `VERIFY_ALWAYS`; reports nanoseconds to start vforked process and fails if children were invoked but none waited successfully.
