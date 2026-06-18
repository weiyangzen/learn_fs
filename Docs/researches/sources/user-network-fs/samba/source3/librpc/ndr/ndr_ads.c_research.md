# sources/user-network-fs/samba/source3/librpc/ndr/ndr_ads.c

## Purpose
`ndr_ads.c` supplies custom NDR push/pull routines for `ads_struct`.

## Important APIs, types, and functions
- `ndr_pull_ads_struct()` returns `NDR_ERR_SUCCESS` without reading fields.
- `ndr_push_ads_struct()` returns `NDR_ERR_SUCCESS` without writing fields.

## Control flow
Both functions are no-op success stubs. They satisfy generated linker/API expectations for an IDL type that is marked mostly `nopush,nopull` and used as C-side state rather than serialized data.

## State and persistence behavior
No state is serialized or deserialized. Passing an `ads_struct` through NDR with these hooks intentionally drops all contents.

## Dependencies and integration points
The file includes generated `ndr_ads.h` and is compiled into `NDR_ADS` alongside generated `ndr_ads.c`. `libnet_join.idl` can refer to `ads_struct *` without requiring real marshalling.

## Risks and edge cases
Callers must not expect `ads_struct` contents to cross an NDR boundary. These no-op hooks are safe only if every use is local/C-only. A future real RPC use would need actual marshalling and compatibility review.

## Test signals
Build/link tests should confirm custom hooks satisfy generated references. Negative design tests should ensure no network path depends on serialized ADS connection state.
