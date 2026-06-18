# File Research: sources/os/plan9/plan9/sys/src/9/port/devproc.c

Implements `#p`, the process filesystem. Top-level entries are `trace` and one directory per live process pid. Per-process files include `args`, `ctl`, `fd`, `fpregs`, `kregs`, `mem`, `note`, `noteid`, `notepg`, `ns`, `proc`, `regs`, `segment`, `status`, `text`, `wait`, `profile`, and `syscall`.

Qids encode file type, process slot, and pid/version for stale-channel detection. `procgen` enumerates processes, builds per-process file permissions from static `procdir` permissions plus `p->procmode`, and computes dynamic lengths for wait/profile files.

Access control is strict around cross-process inspection: user `none` cannot inspect/control other processes unless `eve`; private-memory processes deny `mem`, `ctl`, and `note`; many operations require matching process owner or `eve`. Opening `text` returns the underlying executable channel rather than the synthetic proc channel.

Reads provide process args, syscall trace text, user memory or selected kernel memory through `mem`, profiling buffers, queued notes, raw `Proc`, user/kernel/fp registers, status records, segment listings, wait records, namespace reconstruction, note id, fd table, and global trace events. Directory reads are normal devdir reads.

Writes allow changing args, writing stopped-process memory/registers/fpregs, posting notes, changing noteid, group notes through `notepg`, and extensive control through `ctl`. `procctlreq` supports killing, stopping/waiting, starting with tracing, closing fds, priority/fixed priority, wired processor, noswap/private/hang flags, profiling allocation, scheduler trace toggling, and EDF real-time parameters/admission/expulsion.

`procctlmemio` performs controlled user memory access by locating segments, faulting pages in, mapping pages, copying bytes, converting text to data for writes, and marking TLB/text-cache flush state. `txt2data` and `data2txt` convert segment types while preserving image metadata.

The file also implements global process trace buffering (`Traceevent` ring), per-process profiling clock hooks, namespace mount scanning, fd table formatting used by `devdup`, and wait queue consumption. This is one of the broadest kernel introspection/control surfaces in the group.
