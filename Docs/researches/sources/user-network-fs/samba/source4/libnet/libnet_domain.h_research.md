# sources/user-network-fs/samba/source4/libnet/libnet_domain.h

## Purpose
`libnet_domain.h` declares the request/result structures for opening, closing, and listing SAMR/LSA domains through libnet.

## Important APIs, Types, And Functions
`enum service_type` selects `DOMAIN_SAMR` or `DOMAIN_LSA`. `struct libnet_DomainOpen` contains input service type, domain name, and access mask, and returns a policy handle plus error string. `struct libnet_DomainClose` identifies which cached service/domain handle should be closed. `struct libnet_DomainList` takes a hostname and returns a count plus an array of `domainlist { sid, name }`. `struct msg_rpc_lookup_domain` is a monitor payload containing a domain name looked up over RPC.

## Control Flow
The structures map directly to `libnet_domain.c`: open dispatches by service type, close dispatches by service type, and list enumerates SAMR domain databases on a host. The header itself contains no logic.

## State And Persistence Behavior
The types carry handles and error strings but do not own persistent state. The implementation stores successful handles in `libnet_context`, so consumers of this header should treat the returned handle as part of a broader context-owned session.

## Dependencies And Integration Points
The header relies on generated/standard Samba types such as `policy_handle`. It is consumed by libnet modules that need a domain handle before performing SAMR/LSA operations, including group and lookup helpers.

## Risks
The output `domainlist.sid` field may be null depending on implementation path. Callers must set `type`, `domain_name`, and appropriate access masks, and must not assume the returned policy handle remains valid after `libnet_DomainClose`.

## Test Signals
Compile tests should catch enum/struct contract changes. Functional tests should verify SAMR and LSA open/close callers populate and clear these structures consistently and that domain-list consumers tolerate null SID strings.
