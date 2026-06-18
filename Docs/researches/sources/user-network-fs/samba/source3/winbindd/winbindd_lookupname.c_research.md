# sources/user-network-fs/samba/source3/winbindd/winbindd_lookupname.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_lookupname.c

`winbindd_lookupname.c` implements the asynchronous external `WINBINDD_LOOKUPNAME` command, converting a domain/name or qualified username into a SID and LSA SID type. Its state object stores the event context, returned `dom_sid`, and `lsa_SidType`.

`winbindd_lookupname_send()` validates string termination for `request->data.name.dom_name` and `.name`, parses the request into `namespace`, `domname`, and `name`, and supports three input styles: an explicit domain field, a fully qualified name split by `lp_winbind_separator()`, and a UPN-like value containing `@`. If no domain or UPN realm is present, namespace is empty and lookup falls through normal routing. It then starts `wb_lookupname_send(state, ev, namespace, domname, name, 0)`. `winbindd_lookupname_done()` receives the SID/type with `wb_lookupname_recv()` and propagates errors through tevent. `winbindd_lookupname_recv()` fills `response->data.sid.sid` using `sid_to_fstring()` and `response->data.sid.type`.

No durable state is stored. The command depends on parse-time mutation of the request buffer when splitting `DOMAIN\user`; this is safe inside request handling but worth noting for callers expecting the original string. Dependencies include tevent, `dom_sid`, loadparm separator configuration, `wb_lookupname_*`, and winbind domain routing/caches in lower layers. Integration points are NSS/PAM/client SID lookup calls and the shared async command dispatch pattern.

Risks are ambiguous names when a separator or `@` appears in unexpected positions, separator changes, and failure logging that says "Could not convert SID" although the operation is name-to-SID. Test signals include explicit domain lookups, separator-qualified names, UPN names, default-domain names, unknown names, and response type preservation for users/groups/aliases.
