# File Research: sources/os/plan9/9front/sys/src/9/mt7688/main.c

This is the MT7688 kernel bootstrap and machine initialization file. It declares global `Conf`, `machaddr`, initial FP save state, and the per-machine software TLB array.

`main` initializes console UART, formatting, memory configuration, `Mach`, active CPU state, kmap, allocators, timers, plan9.ini, interrupts, CPU identification, page mask, TLB, pages, processes, segments, device links, channel devices, the initial user process, and finally enters the scheduler.

`machinit` sets up `MACHP(0)`, clears `Mach`, initializes CPU speed/hz guesses, binds `m->stb` to the software TLB, installs exception handler pointers at `SPBADDR`, copies vector stubs into `KSEG0` vector addresses, clears BEV, disables CU1/FPU state, and calls `clockinit`.

`init0` initializes channel devices and environment variables, starts the alarm kproc, builds the initial `/boot` user stack, and calls `touser`. `confinit` partitions fixed 128 MB memory between kernel and user pages and sizes process/image/swap pools. `exit` clears secrets on CPU 0 and halts.

Filesystem relevance is high: this file decides memory pool sizing, initializes the page allocator, channels, device table, and first user process that mounts/boots the namespace.

Notable risks: CPU/memory values are hardcoded for the target board; `fmtinit` is unused; some debug checks remain; `confinit` computes kernel pages before setting `conf.nproc`, which mirrors old Plan 9 patterns but is easy to misread.
