## sources/test-tools/syzkaller/prog/resources.go

Purpose: computes resource constructors, resource compatibility, input resources, and the transitive set of syscalls that can be generated when dependencies are satisfied.

Important APIs/types/functions: `timespecRes`, `filenameRes`, `vmaRes`, `Target.calcResourceCtors`, `populateResourceCtors`, `isCompatibleResource`, `isCompatibleResourceImpl`, `getInputResources`, `transitivelyEnabled`, and `TransitivelyEnabledCalls`.

Control flow: `populateResourceCtors` scans syscall types to collect created resources, used resources, and input resources, adds special `clock_gettime` support for timespec, then populates precise and imprecise constructors based on resource-kind prefix compatibility. Transitive enablement repeatedly adds calls whose input resources can already be created.

State and persistence: fills per-target in-memory syscall fields (`inputResources`, `createsResources`, `usesResources`) and resource constructor lists.

Dependencies/integration: depends on restored resource descriptors, `ForeachCallType`, target OS checks, and is used by generation, rotation, and enabled-call filtering.

Risks: optional resources are intentionally skipped for dependency disabling; mistakes can over-disable or under-disable syscalls. Compatibility is prefix-based, so resource kind ordering is critical.

Test signals: `resources_test.go` checks constructor availability, linux epoll dependency behavior, automatic calls, optional resource handling, timespec disabling via `clock_gettime`, resource creation under rotated and partial syscall sets, and precise constructor preference.
