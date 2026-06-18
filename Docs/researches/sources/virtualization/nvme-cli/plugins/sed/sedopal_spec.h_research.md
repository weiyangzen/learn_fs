# File Research: sources/virtualization/nvme-cli/plugins/sed/sedopal_spec.h

TCG Opal/Ruby/Pyrite discovery specification layout header.

Main contents:
- `enum sed_status_codes`: method status codes used by `sedopal_error_to_text`.
- Internal feature bitmask constants for parsed feature presence.
- Level 0 discovery feature codes from TCG Opal specifications.
- Locking feature bits: supported, enabled, locked, media encryption, MBR enabled/done.
- Packed discovery structures:
  - `level_0_discovery_header`
  - `level_0_discovery_features`
  - `tper_desc`
  - `locking_desc`
  - `geometry_reporting_desc`
  - `opalv1_desc`
  - `opalv2_desc`
  - `single_user_mode_desc`
  - `datastore_desc`
  - `opalite_desc`
  - `pyrite_v1_desc`
  - `pyrite_v2_desc`
  - `ruby_desc`
  - `locking_lba_desc`
  - `block_sid_auth_desc`
  - `config_ns_desc`
  - `data_removal_desc`
  - `ns_geometry_desc`

Storage relevance:
- These structures describe device encryption/locking capabilities and logical block geometry that can affect namespace and filesystem access policy.
- All multi-byte descriptor fields are big-endian and are converted in `sedopal_cmd.c`.
