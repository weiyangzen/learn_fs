# sources/test-tools/syzkaller/vm/vmimpl/linux.go

Purpose: Linux-specific post-crash diagnostic helper for reports that need extra VM-side state.

Important APIs/types/functions: `DiagnoseLinux(rep *report.Report, ssh func(args ...string) ([]byte, error))`.

Control flow: checks the report title for `MAX_LOCKDEP`; if absent, returns unhandled. For lockdep-capacity reports, it runs `cat /proc/lockdep_stats /proc/lockdep /proc/lockdep_chains` through the supplied SSH callback, records any command error as bytes, strips large pointer-like hex values with a regexp, and returns the output with `handled=true`.

State and persistence: no persistent state; only reads procfs from the guest through SSH.

Dependencies and integration: depends on `pkg/report` and a backend-provided SSH function. Integrated from VM backends that can diagnose Linux guests.

Risks: narrow trigger substring; proc files can be huge or unavailable; regexp may remove useful numeric context; command failures become text rather than errors.

Test signals: no direct assigned test. Monitor tests cover diagnostic plumbing generically, not this Linux-specific command.
