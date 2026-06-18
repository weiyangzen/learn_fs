# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.y

Hand-authored Bison grammar for Open Firmware / OBP boot paths. It includes `prom_parse.h` and `iscsi_obp.h`, defines `YYSTYPE` as a large string buffer, enables locations, and passes `struct ofw_dev *ofwdev` into parse actions.

Top-level `devpath` alternatives cover `/`, physical bus chains plus boot device, optional disk labels, optional OBP qualifiers and parameters, and a virtual-device path form. For physical boot-device paths, actions allocate and store `ofwdev->dev_path` as `/<busses><bootdev>`, omitting disk labels and parameter suffixes.

The grammar builds path component strings for buses, boot devices, virtual-device parameters, OBP qualifier lists, OBP parameter lists, IPv4/IPv6 addresses, hex sequences, disk labels, and disk partitions.

OBP parameter actions have side effects on `ofwdev`: numeric/hex parameters call `obp_parm_hexnum`, IP parameters call `obp_parm_addr`, IQNs call `obp_parm_iqn`, filenames call `obp_parm_str`, and qualifiers call `obp_qual_set`.

Notable constraints: semantic buffers are fixed at 16384 bytes; most concatenations use `snprintf`, but some copies use `strcpy` where the lexer’s token length bounds are assumed to keep data safe. `malloc` results for `dev_path` are not checked.
