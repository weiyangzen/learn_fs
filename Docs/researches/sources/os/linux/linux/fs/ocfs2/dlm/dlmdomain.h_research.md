# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.h

## Purpose
Small header for domain-global state and domain status helpers.

## Exposed API
- Externs `dlm_domain_lock` and `dlm_domains`.
- `dlm_joined()` checks for `DLM_CTXT_JOINED` under `dlm_domain_lock`.
- `dlm_shutting_down()` checks for `DLM_CTXT_IN_SHUTDOWN`.
- Declares `dlm_fire_domain_eviction_callbacks()`.

## Notes
The inline helpers centralize protected reads of `dlm->dlm_state` for users that only need boolean domain state.
