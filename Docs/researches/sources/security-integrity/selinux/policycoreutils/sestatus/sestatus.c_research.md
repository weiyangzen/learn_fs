<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.c -->
# sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.c

## Purpose
Reports SELinux system status, optional boolean state, and optional verbose process/file context checks.

## Important APIs, Types, And Functions
Important helpers are `cmp_cmdline()`, `pidof()`, `load_checks()`, and `printf_tab()`. It uses libselinux status/config APIs (`is_selinux_enabled`, `selinux_mnt`, `selinux_path`, `selinux_policy_root`, `security_getenforce`, `selinux_getenforcemode`, `is_selinux_mls_enabled`, `security_deny_unknown`, `security_get_checkreqprot`, `security_policyvers`, boolean APIs, `getcon`, `getpidcon`, `lgetfilecon`, `getfilecon`) plus `/proc` directory scanning.

## Control Flow
`main()` parses `-v` and `-b`, prints core SELinux mount/root/policy/mode/MLS/deny_unknown/checkreqprot/policy version state, optionally lists active and pending booleans, and exits unless verbose mode is enabled. In verbose mode it loads process and file checks from `/etc/sestatus.conf`, prints current and init process contexts, looks up configured process executables by scanning `/proc`, then prints controlling terminal and configured file/symlink contexts.

## State And Persistence
The tool is read-only. It dynamically allocates check lists from the config file and frees them while reporting.

## Dependencies And Integration Points
It integrates with `/etc/sestatus.conf`, SELinuxfs, `/proc/<pid>/exe`, and libselinux runtime/config status.

## Risks And Edge Cases
`cmp_cmdline()` uses fixed-size buffers and `readlink` without the return length, though it forces termination. `ttyname(0)` can be NULL, causing context lookup failures. The config loader caps each section at 50 entries and ignores overflow.

## Test Signals
Exercise disabled SELinux, missing selinuxfs, `-b` boolean output, `-v` with missing and populated config, symlink file checks, long command paths, and no controlling terminal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.c -->
