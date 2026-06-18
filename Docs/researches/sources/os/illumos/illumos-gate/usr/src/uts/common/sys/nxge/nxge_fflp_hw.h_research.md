# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hw.h

## Purpose
Defines the hardware ABI for the NXGE Fast Frame Lookup Processor, including VLAN table registers, programmable L2/L3 class registers, TCAM key/mask/control/result formats, FCRAM/hash registers, flow-key registers, error logs, and in-memory entry layouts for TCAM and FCRAM operations.

## Main Interfaces
- VLAN table hardware:
  - `FFLP_ENET_VLAN_TBL_REG`
  - `fflp_enet_vlan_tbl_t`
- TCAM programmable class registers and structures:
  - `tcam_class_prg_ether_t`
  - `tcam_class_prg_ip_t`
  - `tcam_class_t`
  - L3 programmable class masks/shifts for RF-NIU/Neptune-L.
- TCAM key/control/result:
  - `FFLP_TCAM_KEY_*`
  - `FFLP_TCAM_MASK_*`
  - `FFLP_TCAM_CTL_REG`
  - `tcam_class_key_ip_t`
  - `tcam_ctl_t`
  - `tcam_res_t`
  - `tcam_ipv4_t`, `tcam_ipv6_t`, `tcam_ether_t`, `tcam_reg_t`, `tcam_entry_t`
- Error hardware:
  - `vlan_par_err_t`
  - `tcam_err_t`
  - `hash_lookup_err_log1_t`
  - `hash_lookup_err_log2_t`
  - `fflp_err_mask_t`
  - `hash_tbl_data_log_t`
- FFLP global config and FCRAM timing:
  - `fflp_cfg_1_t`
  - `fcram_ref_tmr_t`
  - `fcram_phy_rd_lat_t`
- Flow hash configuration:
  - `flow_class_key_ip_t`
  - `hash_h1poly_t`
  - `hash_h2poly_t`
  - `flow_prt_sel_t`
  - `flow_template_t`
  - `flow_key_cfg_t`
  - `tcam_key_cfg_t`
- FCRAM entry formats:
  - `hash_optim_t`
  - `hash_hdr_t`
  - `hash_ports_t`
  - `hash_match_action_t`
  - `hash_ipv4_t`
  - `hash_ipv6_t`
  - `fcram_entry_t`
  - `fcram_entry_format_t`
- PIO helper macros for reading/writing TCAM and hash registers.

## Dependencies And Relationships
Includes `nxge_defs.h` and later `netinet/in.h` for address structures in flow templates and hash entries. It supplies the hardware types used by `nxge_fflp.h`, FFLP NPI code, and classification routines declared in `nxge_impl.h`.

## Research Notes
This header is layout-sensitive and heavily endian-conditional. It contains some duplicate and typo-preserving symbols, such as repeated `FCRAM_LOOKUP_HIGH_PRI`, repeated `TCAM_LOOKUP_HIGH_PRI`, duplicated `HASH_ENTRY_TYPE_OPTIM_IP4`, and `FCRAM_ENTRY_UNKOWN`; consumers may depend on those exact names.
