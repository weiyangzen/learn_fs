<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.h -->
# sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.h

Purpose: defines public WINS replication client structures, flag helpers, and includes generated prototypes.

Important APIs and types: forward declarations for `wrepl_request` and `wrepl_socket`, `wrepl_send_ctrl`, `wrepl_associate`, `wrepl_associate_stop`, `wrepl_pull_table`, `wrepl_address`, `wrepl_name`, and `wrepl_pull_names`. Macros decode and construct WINS replication record flags: `WREPL_NAME_TYPE`, `WREPL_NAME_STATE`, `WREPL_NAME_NODE`, `WREPL_NAME_IS_STATIC`, and `WREPL_NAME_FLAGS`.

Control flow: no executable flow. The header shapes inputs and outputs for association setup, stop, table pull, and full name pull. It imports NBT and WINSREPL generated NDR definitions, then includes `winsrepl_proto.h`.

State and persistence: output structs carry association context, partner arrays, and pulled replicated names with version IDs and address lists. Ownership is handled by the implementation's talloc moves.

Risks: flag macros assume bit layout from generated WINSREPL constants; changes in protocol definitions require keeping these masks aligned. Test signals include compile coverage of generated prototypes, flag round-trip tests, and multi-address name representation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.h -->
