# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/config.c

Provides JSON configuration lookup helpers for telemetry parsing.

Main functions:
- `sldm_config_get_struct_by_key_version()` finds a named structure and version.
- `solidigm_config_get_struct_by_token_version()` converts numeric token to string and delegates.
- `solidigm_config_get_nlog_obj_name()` maps telemetry object UIDs to NLOG object names.
- `solidigm_config_get_nlog_formats()` returns the `NLOG_FORMATS` object.
- `sldm_get_enum_label_by_value()` recursively searches a structure definition for enum labels.

Version matching:
- Tries exact major/minor.
- Falls back to minor wildcard `"*"`.
- Also recognizes special wildcard-like numeric keys `"47837"` and `"49374"`, used by SKHT code.

Risks/notes:
- Enum lookup uses recursive descent over `memberList` and returns `"UNKNOWN_ENUM_VALUE"` when missing.
- Warnings are emitted for major version found but missing requested minor.
