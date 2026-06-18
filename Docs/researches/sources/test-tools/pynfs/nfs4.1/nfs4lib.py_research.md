# sources/test-tools/pynfs/nfs4.1/nfs4lib.py

## Purpose
`nfs4lib.py` is the central utility library for pynfs NFSv4.1 code. It wraps generated XDR packers/unpackers, converts attribute bitmaps and fattr structures, defines common NFS exceptions and principals, implements SSV security-context helpers, parses NFS URLs and paths, provides special stateids, and declares attribute access metadata.

## Important APIs, Types, And Functions
- Special stateids `state00`, `state11`, and `state01` are generated `stateid4` values used throughout tests and server code.
- Hash/encryption OID dictionaries and `_e_wrap` support SSV state protection with hashlib and AES.
- `set_attrbit_dicts()` builds `attr2bitnum`, `bitnum2attr`, `bitnum2packer`, and `bitnum2unpacker` from generated `FATTR4_*` constants.
- `set_flags()` builds dictionaries/masks for exchange-id, create-session, and access flags.
- Exception classes `BadCompoundRes`, `UnexpectedCompoundRes`, `InvalidCompoundRes`, `NFS4Error`, and `NFS4Replay` normalize test/server error handling.
- `FancyNFS4Packer` and `FancyNFS4Unpacker` convert bitmap integers, dict-style fattrs, and simple directory-entry lists to/from generated XDR shapes.
- `dict2fattr`, `fattr2dict`, `list2bitmap`, `bitmap2list`, `test_equal`, `inc_u32`, `dec_u32`, `xdrlen`, `verify_time`, `get_nfstime`, `parse_nfs_url`, `path_components`, `attr_name`, `check`, and `use_obj` are broad helper functions.
- `SSVContext` manages SSV subkeys, HMAC MIC tokens, wrap/unwrap encryption tokens, and SET_SSV state.
- `NFS4Principal` is the access-check identity abstraction.
- `AttrConfig` and `attr_info` classify NFSv4 attributes by readable/writeable and object/filesystem/server ownership.

## Control Flow
Import-time initialization creates attribute lookup dictionaries and flag masks. Packing flow passes dict fattrs and integer bitmaps through `FancyNFS4Packer` filters before generated packers run; unpacking reverses the representation. Attribute dict conversion sorts attribute bit numbers, packs values one by one with generated packers, concatenates opaque attr bytes, and builds an `fattr4` with a bitmap.

SSV flow starts with an all-zero SSV. `set_ssv` XORs incoming SSV material with the current SSV, derives subkeys, stores them in a bounded deque, and increments `ssv_seq`. MIC and wrap operations choose initiator-to-target or target-to-initiator keys based on whether the context is local/client-side, pack token plaintext, compute HMACs, and optionally encrypt/decrypt with AES-CBC.

URL parsing accepts optional `nfs://`, one or more comma-separated `host[:port]` servers, bracketed IPv6 addresses, and an optional path. It returns a tuple of `(host, port)` pairs and byte path components normalized by `path_components`.

## State And Persistence Behavior
Most helpers are stateless after import-time dictionaries. `SSVContext` owns mutable key windows, sequence number, and a lock. `NFS4Error` carries protocol status plus attrs, lock-denied, tag, and custom check message. There is no disk persistence.

## Dependencies And Integration Points
The module depends on generated NFSv4 constants/types/packers, `rpc.rpc`, `nfs_ops`, `locking.Lock`, `hashlib`, `hmac`, optional `Crypto.Cipher.AES`, regex/path/time/random/struct utilities, and is imported by nearly every NFSv4.1 client, server, proxy, filesystem, environment, and dataserver module.

## Risks And Edge Cases
- Multiple helpers still use Python 2 string semantics: `ord(c)` over bytes/text, `'\0'` string keys, string joins for binary data, and raising strings.
- `ssv_mech_oid` is a text string while other OIDs are bytes.
- `parse_nfs_url` calls `os.fsencode(m.group('path'))`; if the path group is `None`, it handles it separately, but server host parts remain text.
- `SSVContext.verifyMIC` catches missing old keys with `KeyError`, but deque indexing raises `IndexError`.
- AES is represented by a fake class when PyCrypto is missing; failures occur only when SSV wrap/unwrap is exercised.
- `check` assumes `res.status` and `res.resarray` exist and that status maps contain all values.
- `attr_info` marks many attributes as object/filesystem/server-owned by hand; any generated constant changes require manual updates.

## Test Signals
Signals include fattr dict round trips, bitmap/list conversions, dirlist list/chain conversions, NFS URL parsing for IPv4/IPv6/multipath/default ports, stateid constants, 32-bit sequence wraparound, SSV MIC/wrap/set_ssv behavior with and without AES, `check` exception messages, and attribute ownership/writeability decisions used by `fs.FSObject.set_attrs`.
