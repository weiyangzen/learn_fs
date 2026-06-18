# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/fns.h

Central function prototype header for the drawterm kernel runtime.

Major API groups:
- Channel/device operations: `devattach`, `devwalk`, `devopen`, `devstat`, `devdirread`, `cclose`, `fdtochan`, `namec`, `mntversion`, `mntauth`.
- Queue/block operations: `qopen`, `qread`, `qwrite`, `qbread`, `qbwrite`, `allocb`, `freeb`, `pullupblock`, `padblock`, `trimblock`.
- Process/scheduler operations: `newproc`, `ready`, `sched`, `sleep`, `wakeup`, `postnote`, `pexit`.
- Memory/page/segment operations: `newpage`, `putpage`, `segattach`, `fault`, `flushmmu`, `malloc`, `smalloc`.
- Console/input/draw support: `printinit`, `kbdputc`, `readstr`, `readnum`, `drawactive`, `screeninit`.
- Time/random/system helpers: `todget`, `todset`, `fastticks`, `randomread`.
- Command parsing: `parsecmd`, `lookupcmd`, `cmderror`.
- Host integration: `oserrstr`, `oserror`, `osproc`, `osnewproc`, `osinit`.

Notable details:
- Defines `malloc` as `kmalloc`.
- Defines `waserror()`/`poperror()` using the drawterm setjmp-based error stack.
- Defines `islo()` as `0`, reflecting drawterm’s simplified interrupt-level model.
