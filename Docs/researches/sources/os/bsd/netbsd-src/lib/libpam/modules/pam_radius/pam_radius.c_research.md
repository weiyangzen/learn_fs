# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/pam_radius.c

Read completely: 389 lines.

This authentication module delegates password authentication to a RADIUS server through `radlib`. Options include `conf`, `template_user`, `nas_id`, and `nas_ipaddr`.

`build_access_request` creates a `RAD_ACCESS_REQUEST` with user, password, NAS identifier, NAS IP address, state, and `RAD_AUTHENTICATE_ONLY` service type. It defaults NAS identifier/IP input to the local hostname when applicable.

`pam_sm_authenticate` fetches user and password, opens/configures the RADIUS handle, sends the access request, then handles accept, reject, challenge, and transport errors. On accept, `do_accept` may update `PAM_USER` from a returned `RAD_USER_NAME`; `template_user` can map authenticated users without local passwd entries to a configured local account. On challenge, `do_challenge` displays up to ten reply messages, prompts for a response, includes returned `RAD_STATE`, and resubmits.

Security/reliability notes: challenge-message cleanup is incomplete on several error returns, causing leaks. `template_user` is a powerful identity mapping option and should be restricted to stacks that expect shared local accounts.
