# sources/test-tools/stress-ng/stress-set.c

Purpose: implements the `set` stressor, exercising a broad set of identity, process-group, hostname/domain, time, signal-mask, filesystem uid/gid, group-list, and resource-limit setter system calls with valid and invalid inputs.

Important APIs/types/functions: `stress_set`, `stress_rlimit_info_t`, `rlimit_resources`, `stress_capabilities_check`, `getrlimit`, `setrlimit`, `setsid`, `setgid`, `setuid`, `sethostname`, `setpgid`, `settimeofday`, `setpgrp`, `setgroups`, `setreuid`, `setregid`, `setresuid`, `setresgid`, `setfsgid`, `setfsuid`, `shim_sgetmask`, `shim_ssetmask`, `shim_setdomainname`, and `shim_stime`.

Control flow: the stressor snapshots existing resource limits, allocates hostname buffers, captures current hostname/domain context, synchronizes start, then loops through many setter APIs. It usually restores current values after valid calls and deliberately issues invalid or privilege-requiring calls to exercise error paths. It periodically checks that unprivileged `setreuid`/hard-limit raises do not unexpectedly succeed, and it calls `stime` only once to avoid repeated clock changes.

State and persistence behavior: it touches process credentials, groups, process group/session state, host/domain names, resource limits, and time APIs. Most calls use current values or restore snapshots; hostname/domain/time calls are guarded by capability expectations and error tolerance.

Dependencies and integration points: registered as `CLASS_OS`, always verify. It depends on capability checks (`SHIM_CAP_SYS_RESOURCE`, `SHIM_CAP_SETUID`, `SHIM_CAP_SYS_TIME`), platform headers for fsuid and groups, stress-ng shim wrappers, and saved rlimit state.

Risks and test signals: this is privilege-sensitive and can behave differently under root, containers, Cygwin, or restricted capabilities. Real signals include setters succeeding without required capability, unexpected errno values, inability to restore limits, allocation failure, or platform-specific setters changing global host/domain state.
