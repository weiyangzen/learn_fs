# sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsid.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsid.c

`winbindd_lookupsid.c` implements the asynchronous external `WINBINDD_LOOKUPSID` command, converting one textual SID into a domain name, account name, and LSA SID type. The state carries the parsed SID and the returned domain/name/type pointers.

`winbindd_lookupsid_send()` ensures the SID request field is terminated, parses it with `string_to_sid()`, and starts `wb_lookupsid_send()`. Invalid SID syntax is returned immediately as `NT_STATUS_INVALID_PARAMETER`. `winbindd_lookupsid_done()` receives results with `wb_lookupsid_recv()`, tallocs returned strings under the state, and propagates any NTSTATUS error. `winbindd_lookupsid_recv()` writes `response->data.name.dom_name`, `response->data.name.name`, and `response->data.name.type`.

The file has no durable state and relies on lower-level lookup code for cache use, domain routing, and fallback behavior. Dependencies include tevent, SID parsing/formatting, `wb_lookupsid_*`, and fixed-size response string helpers (`fstrcpy`). Integration points are winbind NSS SID-to-name calls, `wbinfo --sid-to-name` style clients, and the shared async command dispatch.

Risks are mostly input and truncation related: malformed SID strings must be rejected, response names can be truncated to fixed fields by `fstrcpy`, and the command returns a single status rather than carrying partial data. Test signals include malformed SID text, well-known/internal/domain SIDs, unmapped SIDs, alias/group/user SID types, and long returned names.
