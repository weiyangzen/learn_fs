# sources/test-tools/strace/src/rtnl_dcb.c

Purpose: Decodes DCB route-netlink messages.

Important APIs/types/functions: route decoder for DCB family messages and DCB attribute decoder table.

Control flow: prints the fixed DCB message fields, then delegates aligned DCB attributes to `decode_nlattr` using DCB xlat names and simple scalar/string decoders where known.

State and persistence: stateless.

Dependencies/integration: DCB Linux UAPI headers, route-netlink dispatcher, and nlattr helpers.

Risks: DCB has many nested/vendor-specific attributes that may remain generic. Short headers and unknown attrs must remain robust.

Test signals: DCB get/set messages with known attrs, nested unknown payload, and malformed lengths.
