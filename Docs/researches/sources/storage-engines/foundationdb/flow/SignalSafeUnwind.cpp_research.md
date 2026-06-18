<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SignalSafeUnwind.cpp -->
# sources/storage-engines/foundationdb/flow/SignalSafeUnwind.cpp
- Purpose: Wraps `dl_iterate_phdr` on Linux non-sanitizer builds so profiling is disabled while unwinding shared-object headers, reducing unsafe signal interaction.
- Important APIs/types/functions: Global `dl_iterate_phdr_calls`, `initChain`, overridden `extern "C" dl_iterate_phdr`, `chain_dl_iterate_phdr`, `setProfilingEnabled`, and `criticalError`.
- Control flow: The override increments the call counter, lazily resolves the next `dl_iterate_phdr` implementation with `dlsym(RTLD_NEXT, ...)`, disables profiling, calls the real function, re-enables profiling, and returns the real result.
- State and persistence behavior: State is process-local: a counter and cached function pointer protected by `std::once_flag`. Nothing is persisted.
- Dependencies and integration points: Integrates with ELF dynamic loader behavior, Flow profiling enablement, and fatal error handling. Sanitizer builds disable the workaround because sanitizer initialization itself calls `dl_iterate_phdr`.
- Risks: Function interposition is platform/linker sensitive. If `dlsym` fails the process exits via `criticalError`. Re-enabling profiling is not exception-protected, but the C callback path is expected not to throw.
- Test signals: Linux dynamic-link tests should confirm the override resolves and forwards correctly. Sanitizer builds should compile without the override. Profiling tests should observe `dl_iterate_phdr_calls` when profiler metadata is collected.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SignalSafeUnwind.cpp -->
