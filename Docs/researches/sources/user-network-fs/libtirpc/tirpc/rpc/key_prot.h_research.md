# sources/user-network-fs/libtirpc/tirpc/rpc/key_prot.h

Purpose: `key_prot.h` is rpcgen output for the keyserv/key protocol used by AUTH_DES/Diffie-Hellman secure RPC.

Important APIs, types, and functions: It defines key constants (`KEY_PROG`, versions 1/2, `KEYSIZE`, `HEXKEYBYTES`), `enum keystatus`, `keybuf`, `netnamestr`, request/result structs for encrypt/decrypt/getcred/netst operations, procedure numbers, client and service stubs for versions 1 and 2, free-result helpers, and XDR functions for every protocol type.

Control flow: Clients call generated stubs such as `key_set_1`, `key_encrypt_2`, or `key_get_conv_2` with a `CLIENT`; servers implement `_svc` counterparts for the same procedure numbers. XDR functions marshal strings, DES blocks, netobjs, Unix credentials, and discriminated result unions.

State and persistence behavior: Header structs hold secrets, public/private key strings, netnames, DES session keys, and Unix credential arrays, but runtime persistence belongs to keyserv implementations. Generated client stubs may return pointers to static result storage depending on rpcgen conventions.

Dependencies and integration points: It includes `rpc/rpc.h` and uses `des_block`, `netobj`, `CLIENT`, `SVCXPRT`, and `struct svc_req`. AUTH_DES utilities in `auth.h` call keyserv APIs.

Risks: The file is generated and should not be hand-edited; changes should come from the `.x` source. It transports sensitive key material and obsolete DES-era secrets. RPC stub static storage and generated free-result ownership are common concurrency/lifetime pitfalls.

Test signals: Tests should cover rpcgen regeneration consistency, XDR round trips for every type, version 1/2 procedure number compatibility, service/client stub linkage, and secret material cleanup in implementation paths.
