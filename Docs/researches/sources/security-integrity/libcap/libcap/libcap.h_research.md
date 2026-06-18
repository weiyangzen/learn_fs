## sources/security-integrity/libcap/libcap/libcap.h

Purpose: private internal header defining libcap object layouts, magic values, locking primitives, capability bit macros, generated name integration, syscall hooks, launcher internals, and validation helpers.

Important APIs/types/macros: `_cap_struct`, `cap_iab_s`, `cap_launch_s`, `CAP_T_MAGIC`, `CAP_S_MAGIC`, `CAP_IAB_MAGIC`, `CAP_LAUNCH_MAGIC`, `_cap_mu_*` locks, `raise_cap/lower_cap/isset_cap`, `LIBCAP_EFF/INH/PER`, debug macros, `psx_load_syscalls`, `EXECABLE_INITIALIZE`, static assertion support, and `good_cap_*` validation helpers in the later part of the file.

Control flow: compile-time selection validates kernel capability version constants, defines internal data representations and helper macros used by all `.c` files.

State/persistence: describes heap object memory layout and process-global syscall override flag; no standalone runtime code except declarations/macros.

Dependencies/integration: public `sys/capability.h`, generated `cap_names.h`, scheduler/yield for spin locks, optional psx library, executable shared-object support.

Risks: internal ABI offset is coupled to allocation/free logic; lock macros are minimal spin locks, not full pthread mutexes; generated header mismatch stops compilation or causes name/text errors.

Test signals: full libcap compile, `cap_test`, sanitizer builds around `cap_free`/validation, and shared-object execution tests.
