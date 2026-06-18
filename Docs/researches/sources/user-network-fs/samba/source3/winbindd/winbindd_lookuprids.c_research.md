# sources/user-network-fs/samba/source3/winbindd/winbindd_lookuprids.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_lookuprids.c

`winbindd_lookuprids.c` implements `WINBINDD_LOOKUPRIDS`, which maps a domain SID plus a newline-separated RID list to principal names and SID types. It is a parent-side async wrapper around the domain child `wbint_LookupRids` call. The state stores the parsed domain SID, returned domain name, `wbint_RidArray`, and returned `wbint_Principals`.

`winbindd_lookuprids_send()` terminates and parses `request->data.sid` with `string_to_sid()`, resolves the target with `find_lookup_domain_from_sid()`, validates that `request->extra_data.data` is NUL-terminated, parses RIDs via `parse_ridlist()`, and sends `dcerpc_wbint_LookupRids_send()` to `dom_child_handle(domain)`. The callback receives both transport and operation status using `dcerpc_wbint_LookupRids_recv()` and `any_nt_status_not_ok()`. The recv path formats each returned principal as `"<type> <name>\n"` in `response->extra_data.data`, sets `response->data.domain_name`, and updates response length.

`parse_ridlist()` counts newline delimiters, allocates a `uint32_t` array, and uses `smb_strtoul(..., SMB_STR_STANDARD)` to reject malformed or non-newline-terminated tokens. An empty list is valid and returns zero RIDs. There is no persistent state; results depend on domain child SAM/LSA lookups and associated caches.

Dependencies include generated `ndr_winbind_c`, SID helpers, `smb_strtox`, domain routing, tevent, and talloc. Risks include rejecting a final RID without a trailing newline, response growth for large RID lists, partial mapping semantics delegated to the child, and domain SID routing failures. Test signals include valid multi-RID input, empty input, malformed RID text, non-terminated `extra_data`, unknown domain SID, unmapped RIDs, and response domain/name/type formatting.
