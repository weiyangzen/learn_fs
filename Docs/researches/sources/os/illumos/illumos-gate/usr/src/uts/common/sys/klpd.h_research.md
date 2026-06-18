# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klpd.h

## Purpose
Defines kernel/user packet formats and kernel-private entry points for kernel-level privilege daemon calls and `pfexec` privilege policy checks.

## Main Interfaces
- Protocol/version constants:
  - `KLPDCALL_VERS`
  - `KLPDARG_*` argument type constants for vnode, integer, and port arguments.
- Kernel-only APIs:
  - `klpd_reg()`, `klpd_unreg()`
  - `klpd_call()`
  - `klpd_freelist()`, `klpd_rele()`
  - credential-held KLPD references via `crklpd_hold()`/`crklpd_rele()`
  - `pfexec_reg()`, `pfexec_unreg()`, `pfexec_call()`
  - `get_forced_privs()`, `check_user_privs()`
- Packet structures:
  - `klpd_head_t`
  - `klpd_arg_t`
  - `pfexec_arg_t`
  - `pfexec_reply_t`
- Offset helpers:
  - `KLH_PRIVSET()`
  - `KLH_ARG()`
  - `PFEXEC_REPLY_IPRIV()`
  - `PFEXEC_REPLY_LPRIV()`

## Dependencies And Relationships
Uses privilege sets, credentials, process-set IDs, pathnames, and variable argument lists. The packet structures are ABI-like layouts shared with daemon or syscall-facing code.

## Research Notes
Most variable-size data is addressed by offsets inside packed buffers, so callers must preserve buffer layout and alignment expectations. `pfexec_reply_t` can return credential changes, environment-scrub policy, authorization status, and initial/limit privilege sets.
