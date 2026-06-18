# sources/user-network-fs/samba/source4/libnet/userman.h

## Purpose

`userman.h` declares the caller-facing IO structures and field masks consumed by `userman.c` for SAMR-backed user add, delete, and modify operations. It also defines monitor payload structures emitted by those operations.

## Important APIs And Types

`struct libnet_rpc_useradd` carries input `domain_handle` and `username`, with output `user_handle`. `struct libnet_rpc_userdel` has the same input and output shape. `struct libnet_rpc_usermod` carries input `domain_handle`, target `username`, and nested `struct usermod_change`.

The `USERMOD_FIELD_*` constants define a bitmask for requested changes. They include account name, full name, description, comment, home directory/drive, logon script, profile path, workstations, logon hours, account expiry, account flags, parameters, country code, and code page. The nested change struct provides strings, several time values, and account flags; not every declared mask has a corresponding value or implementation in `userman.c`.

Monitor payloads include `msg_rpc_create_user` with a RID and `msg_rpc_lookup_name` with RID array pointer and count. Other monitor structures referenced by `userman.c`, such as open-user messages, come from broader libnet headers.

## Control Flow And State

The header is passive. Its structures are filled by callers and copied into per-operation state in `userman.c`. The `fields` bitmask acts as the state cursor for modification: `userman.c` clears bits as fields are successfully mapped into SAMR info levels.

## Dependencies And Integration Points

The only direct include is `librpc/gen_ndr/misc.h` for `policy_handle` and related generated types. Consumers are the libnet RPC user-management functions built into `samba-net`.

## Risks

The header advertises more change masks than the implementation handles, which can surprise callers with `NT_STATUS_INVALID_PARAMETER`. Time fields such as password-change and logon timestamps are present in the struct but are not mapped in the observed `userman.c` code. Callers must keep `username` and string pointers valid until the send function has copied or consumed them.

## Test Signals

Compile-time tests should catch ABI-impacting layout changes. Runtime tests should assert that each documented flag either succeeds with a known SAMR level or returns a clear invalid-parameter error when unsupported.
