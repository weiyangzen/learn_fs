# sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsids.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsids.c

`winbindd_lookupsids.c` implements `WINBINDD_LOOKUPSIDS`, a batch SID-to-name command. Its state stores a parsed SID array and the returned `lsa_RefDomainList` plus `lsa_TransNameArray`. It exists to amortize lookup overhead and return enough domain-reference metadata for clients to interpret translated names.

`winbindd_lookupsids_send()` requires non-empty `extra_data`, validates NUL termination, parses the SID list with shared `parse_sidlist()`, and calls `wb_lookupsids_send(state, ev, state->sids, state->num_sids)`. The callback receives domain and name arrays via `wb_lookupsids_recv()`. `winbindd_lookupsids_recv()` serializes the result into `extra_data`: first the domain count, then lines of `<sid> <domain-name>`, then the translated-name count, then lines of `<sid_index> <sid_type> <name>`.

There is no local persistence. Lower layers decide cache usage, domain fan-out, and partial translation behavior. Dependencies include tevent, talloc formatting, `parse_sidlist`, LSA generated structures, and SID string helpers. Integration points are high-volume consumers that need many SID translations, including group/token expansion and winbind client tools.

Risks include strict NUL-terminated input requirements, large response allocation, line-oriented output ambiguity if names contain unexpected whitespace, and robustness when lower layers return inconsistent count arrays. Test signals include zero-length rejection, malformed SID list rejection, multiple domains in one response, unknown SID translations, ordering preservation, and response parsing by existing winbind clients.
