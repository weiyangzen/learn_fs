<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_spnupdate -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_spnupdate

Purpose: ensures the local DC computer object has all service principal names from `spn_update_list`.

Important APIs/types/functions: `get_subst_vars`, local `local_update`, RODC `call_rodc_update`, `SamDB`, `secrets.ldb` credential lookup for `SAMDB Credentials`, `drsuapi.DsWriteAccountSpn`, and `samba.substitute_var`.

Control flow: the script loads credentials and tries to open `secrets.ldb` for stored SAMDB credentials, then opens samdb. It builds substitution values, checks whether this DC hosts DomainDnsZones and ForestDnsZones, filters SPN templates accordingly, expands SPNs, searches the DC computer object, computes case-insensitive missing SPNs, and exits if none are needed. RWDCs modify `servicePrincipalName` locally; RODCs find a writable DC and issue a DRS `DsWriteAccountSpn` add request.

State and persistence behavior: mutates the local samdb computer object on RWDCs. On RODCs, changes are sent to a writable DC over sealed DRS. It reads but does not change `spn_update_list` or `secrets.ldb`.

Dependencies and integration points: integrates with Samba AD provisioning, machine credentials, DNS application partition ownership, NetLogon DC discovery, and DRSUAPI.

Risks: missing or wrong `SAMDB Credentials` can prevent local DB access. RODC update filters one DRS replication GUID SPN for unclear protocol reasons. The ForestDnsZones ownership check compares against the domain base DN in this version, which is a subtle source of skipped forest DNS SPNs if naming contexts differ.

Test signals: verbose old/new SPN lists, successful local LDB modify, and DRS `WERR_OK` status are main signals. RODC tests should verify writable DC discovery and replication of added SPNs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_spnupdate -->
