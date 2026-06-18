<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.h -->
# sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.h

Purpose: declares the legacy winbind client adapter functions for SID/Unix ID mapping.

Important APIs and types: includes `librpc/gen_ndr/idmap.h` and declares `wbc_sids_to_xids(struct id_map *ids, uint32_t count)` and `wbc_xids_to_sids(struct id_map *ids, uint32_t count)`.

Control flow: no executable flow. The header allows callers to pass mutable arrays of `id_map` records and receive updated mapping status and values.

State and persistence: no state in the header. The implementation mutates caller-provided maps and talks to winbind.

Risks: there are no include guards in this header, so repeated inclusion depends on the wider build avoiding duplicate prototype issues. Test signals include successful compilation under repeated includes and consumers using the NDR idmap types consistently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.h -->
