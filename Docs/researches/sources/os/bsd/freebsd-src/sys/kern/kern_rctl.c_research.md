# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rctl.c

Read completely: 2247 lines.

## Purpose
Implements FreeBSD's RACCT-backed resource control facility (`rctl`): rule parsing, rule storage, enforcement actions, rule inheritance, credential-change relinking, and the `rctl_*` syscalls.

## Main Elements
- Compiles only under `RCTL` and requires `RACCT`; otherwise exports `sys_rctl_*` stubs returning `ENOSYS`.
- Defines string dictionaries for subject types (`process`, `user`, `loginclass`, `jail`), RACCT resource names, and actions including signals, `deny`, `log`, `devctl`, and `throttle`.
- Maintains `struct rctl_rule` objects in UMA storage and attaches them to RACCT containers via `struct rctl_rule_link`, with rule refcounts and delayed freeing through `taskqueue_thread`.
- Implements throttling parameters and sysctls under `kern.racct.rctl`, including minimum/maximum sleep duration and process/container penalty percentages.
- `rctl_enforce()` evaluates every rule linked to a process for a resource, rate-limits log/devctl notifications, sends signals, applies throttling through `racct_proc_throttle()`, and defers final denial until other side effects have run.
- `rctl_get_limit()`, `rctl_get_available()`, and `rctl_pcpu_available()` expose effective resource ceilings for consumers, with special handling for percent-CPU.
- `rctl_string_to_rule()` parses user rule/filter strings in the form `subject:id:resource:action=amount/per`, resolves process, UID, loginclass, and jail subjects, and converts "millions" RACCT resources.
- `rctl_rule_add()` validates deny/throttle compatibility, removes duplicates, links rules to the subject RACCT, and walks all processes to attach applicable inherited rules.
- `rctl_rule_remove()` removes matching rules from process, user, loginclass, jail, and all-process RACCT lists.
- `sys_rctl_get_racct()`, `sys_rctl_get_rules()`, `sys_rctl_get_limits()`, `sys_rctl_add_rule()`, and `sys_rctl_remove_rule()` implement the privileged user ABI with bounded input/output buffers.
- `rctl_proc_ucred_changed()` rebuilds a process rule-link list after credential changes, preserving per-process rules and retrying if global rule lists change during allocation.
- `rctl_proc_fork()` duplicates process-subject rules for children and links inherited non-process rules; `rctl_racct_release()` tears down all rule links for a RACCT.

## Dependencies And Integration
Tightly integrated with RACCT accounting, process and credential structures, UID/loginclass/jail RACCT containers, allproc locking, `devctl_notify()`, signal delivery, taskqueues, UMA, sysctl/tunables, and privilege checks.

## Risk Notes
Correctness depends on RACCT lock coverage, allproc lock expectations during parsing/add/remove paths, avoiding rule-list races during credential changes, preserving rule refcounts across many container links, and keeping deny/throttle semantics aligned with RACCT resource properties. Output buffers are bounded, so large rule sets can return `ERANGE` or `E2BIG`.
