# sources/test-tools/stress-ng/stress-dynlib.c

Purpose: implements `dynlib`, which stresses dynamic loader operations by repeatedly opening known C library DSOs, resolving symbols, touching resolved code bytes, and closing handles.

Important APIs/types/functions: `stress_lib_info_t` maps compile-time GNU library names from `<gnu/lib-names.h>` to representative symbols. `libnames[]` includes math, pthread, resolver, NSS, rt, util, and related libraries when macros exist. `stress_segvhandler()` uses `siglongjmp` to recover if touching a resolved pointer faults. `stress_dynlib()` owns the dlopen/dlsym/dlclose loop and metric.

Control flow: the stressor installs a SIGSEGV handler, synchronizes start, and loops. Each iteration randomly chooses lazy/now and global/local flags, calls `dlopen()` for each configured library, clears errors, times `dlsym()` lookups for opened handles, reads one byte through `stress_put_uint8()` when a symbol is found, closes all handles, and increments bogo operations.

State and persistence behavior: state is local handle array plus `sigjmp_buf`. No filesystem output or durable state is created. Every iteration closes handles even after a SIGSEGV jump.

Dependencies and integration points: requires `HAVE_LIB_DL` and non-static build; otherwise registers unimplemented. Integrates through `stress_dynlib_info` with classifier `CLASS_OS` and metric `nanosecs per dlsym lookup`.

Risks: symbol sets and GNU DSO macros vary by libc and distribution. Touching function bytes assumes readable mappings, guarded by SIGSEGV recovery. Static builds and non-GNU lib naming cannot exercise this stressor.

Test signals: build dynamic and static variants, run under glibc systems with different available libraries, confirm no leaked handles through repeated runs, and inspect dlsym latency metric.
