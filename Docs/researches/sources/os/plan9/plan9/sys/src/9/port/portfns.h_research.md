# File Research: sources/os/plan9/plan9/sys/src/9/port/portfns.h

Declares the portable kernel function surface for the Plan 9 port.

Coverage:
- Scheduler/process APIs: `sched`, `ready`, `sleep`, `wakeup`, `newproc`, `pexit`, `procctl`, `kproc`, priority and trace helpers.
- VM/page/segment APIs: `newpage`, `putpage`, `cachepage`, `lookpage`, `fault`, `seg`, `newseg`, `dupseg`, `putseg`, `setswapchan`, `swapinit`.
- Device/channel/name APIs: `namec`, `devwalk`, `devopen`, `devstat`, `cclose`, `fdtochan`, `newfd`, `walk`, `unionread`.
- Queue/block APIs: `allocb`, `freeb`, `qopen`, `qread`, `qwrite`, `qbwrite`, `qhangup`, `qclose`, block manipulation helpers.
- Locking and reference APIs: `lock`, `unlock`, `ilock`, `iunlock`, `qlock`, `qunlock`, `rlock`, `wlock`, `incref`, `decref`.
- Time/timer APIs: `timeradd`, `timerdel`, `todget`, `ms2tk`, `tk2ms`, `fastticks` conversions.
- Device-specific portable interfaces: UART, keyboard, draw, watchdog, boot/reboot, random, logging.
- Byte-order helpers: `hnputv`, `hnputl`, `hnputs`, `nhgetv`, `nhgetl`, `nhgets`.

Notable details:
- Contains macro `MS2NS` and `poperror`.
- Declares `ms2tk` twice.
- Includes a non-ASCII `µs(void)` prototype inherited from Plan 9 source.
- Uses Plan 9 vararg checking pragmas for `iprint`, `panic`, and `pprint`.

Role:
- Shared function declaration layer needed by nearly all port C files.
