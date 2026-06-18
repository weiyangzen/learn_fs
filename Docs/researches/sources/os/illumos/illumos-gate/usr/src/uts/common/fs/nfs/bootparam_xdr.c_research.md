# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/bootparam_xdr.c

Implements XDR routines for the bootparam RPC protocol structures used by NFS/network boot paths.

Key elements:
- `xdr_bp_machine_name_t()`, `xdr_bp_path_t()`, and `xdr_bp_fileid_t()` encode/decode bounded bootparam strings using `xdr_string()` with protocol maximums.
- `xdr_ip_addr_t()` encodes/decodes the four byte-style IPv4 address fields: `net`, `host`, `lh`, and `impno`.
- `choices[]` maps `IP_ADDR_TYPE` to `xdr_ip_addr_t()` for the bootparam address union.
- `xdr_bp_address()` encodes/decodes the discriminated `bp_address` union.
- `xdr_bp_whoami_arg()` handles a client address request.
- `xdr_bp_whoami_res()` handles returned client name, domain name, and router address.
- `xdr_bp_getfile_arg()` handles a client name plus file id request.
- `xdr_bp_getfile_res()` handles returned server name, server address, and server path.

Dependencies:
- RPC/XDR APIs from `rpc/rpc.h`: `XDR`, `xdr_string`, `xdr_char`, `xdr_union`, `xdr_discrim`.
- Bootparam protocol types and constants from `rpc/bootparam.h`.

Research notes:
- The routines are direct generated-style XDR serializers with simple short-circuit failure handling.
- `xdr_bp_address()` has only one concrete discriminant, `IP_ADDR_TYPE`; unknown/default union arms use a NULL default handler.
