# sources/storage-engines/rocksdb/monitoring/iostats_context_imp.h

Purpose: Provides internal macros for cheap updates to the thread-local `IOStatsContext`.

Important APIs/types/functions: Declares `extern thread_local IOStatsContext iostats_context` and defines macros `IOSTATS_ADD`, `IOSTATS_RESET`, `IOSTATS_RESET_ALL`, `IOSTATS_SET_THREAD_POOL_ID`, `IOSTATS_THREAD_POOL_ID`, `IOSTATS`, timer guard macros, and `IOSTATS_SET_DISABLE`. In `NIOSTATS_CONTEXT` builds the macros compile away.

Control flow: Update macros directly mutate context fields when `disable_iostats` is false. Timer macros construct `PerfStepTimer` instances on stack, start them, and accumulate elapsed wall or CPU time into IO stats fields.

State/dependencies: The state is the external thread-local context. It depends on `monitoring/perf_step_timer.h` and `rocksdb/iostats_context.h`.

Risks/test signals: Macro expansion assumes a valid field name and can evaluate provided values directly. `IOSTATS_ADD_IF_POSITIVE` is defined only in the disabled branch here, so call sites should not rely on it unless defined elsewhere. `iostats_context_test.cc` validates visible formatting after updates.
