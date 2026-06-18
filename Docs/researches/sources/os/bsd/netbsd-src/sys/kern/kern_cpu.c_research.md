# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_cpu.c

Read completely: 637 lines.

Implements machine-independent CPU attachment, `/dev/cpuctl` ioctl handling, CPU online/offline transitions, interrupt-routing control, CPU class comparison helpers, and optional CPU microcode firmware loading.

`mi_cpu_attach()` assigns CPU indexes, creates per-CPU cpusets, initializes CPU lock/debug lists and names, grows `cpu_infos`, attaches scheduler state, creates the idle LWP, initializes per-CPU subsystems such as percpu, softint, callout, xcall, pool cache, select, and cache state, and increments `ncpu`/`ncpuonline`. `cpuctl_ioctl()` handles get/set CPU state, map ordinal to CPU ID, CPU count, and optional microcode version/apply operations with kauth authorization for state and microcode changes.

`cpu_setstate()` uses cross-calls to run online/offline transitions on the target CPU while `cpu_lock` is held. Offline transition marks `SPCF_OFFLINE`, migrates non-bound/non-interrupt LWPs to an eligible CPU respecting affinity, saves PCU state, suspends heartbeat, and calls MD offline hooks. Online transition resumes heartbeat and clears the offline flag. The code refuses to offline the last online CPU in a processor set. Interrupt control, when supported by the port, uses cross-calls to set or clear `SPCF_NOINTR`, refuses disabling interrupts on the primary CPU, requires at least one interrupt-capable CPU to remain, and redistributes interrupts.

Risks and notes: `IOC_CPU_SETSTATE` calls `cpu_setintr()` and explicitly neglects errors before changing online state. Offline can fail if an affine LWP has no online eligible CPU, in which case the flag is cleared and `EBUSY` is returned. CPU microcode loading frees prior blobs, opens MD firmware, validates nonzero size, allocates firmware memory, and clears state on read failure.
