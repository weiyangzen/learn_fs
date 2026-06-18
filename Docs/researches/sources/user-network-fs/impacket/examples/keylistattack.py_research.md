# sources/user-network-fs/impacket/examples/keylistattack.py

## Purpose

`keylistattack.py` performs the Kerberos KERB-KEY-LIST-REQ attack using an RODC krbtgt number and AES key to recover target account key material without deploying an agent on the target. It can enumerate candidate users over SMB/SAMR or operate on a provided target list.

## Important APIs, Types, and Functions

`KeyListDump.__init__()` stores domain credentials, Kerberos settings, RODC key and number, remote KDC/host settings, enumeration mode, target list, and object handles for SMB, remote operations, and key-list secrets. `connect()` authenticates to SMB with NTLM or Kerberos, allowing a fallback to cached Kerberos tickets when SMB login raises and `KRB5CCNAME` is set. `run()` either enumerates domain users through `RemoteOperations` and `KeyListSecrets` or uses supplied targets, then creates partial TGTs, obtains full TGTs, extracts keys, and prints `domain\user:rid:nthash-like-key`. `getAllDomainUsers()` filters built-in denied RIDs and `krbtgt_` accounts.

## Control Flow

The CLI requires `-rodcNo` and `-rodcKey`. In normal target mode, the target must include `@<KDC>` and valid SMB credentials; the script enumerates allowed users or all users with `-full`. In `LIST` mode, it reads one user or a target file, requires `-kdc`, derives `remoteName` and optionally domain from the FQDN, and skips SMB enumeration. Each target user is converted to a Kerberos `Principal`, passed through `createPartialTGT()`, `getFullTGT()`, and `getKey()`, then printed if a full TGT was returned.

## State and Persistence Behavior

The script writes no files unless stdout is redirected. It reads optional target files and environment variable `KRB5CCNAME`. Remote state is read-only from the script perspective but sends Kerberos requests and may perform SAMR enumeration.

## Dependencies and Integration Points

It depends on Impacket `secretsdump.RemoteOperations`, `secretsdump.KeyListSecrets`, SMB connection handling, Kerberos principals/constants, and `parse_target()`. It integrates with AD KDC/RODC key-list behavior and SAMR domain user enumeration.

## Risks and Edge Cases

Supplying `-full` can be noisy and cause more KDC rejections. LIST-mode target entries from `-t` do not append `:N/A`, while file entries do, so output formatting can differ. `connect()` silently continues after SMB failure when Kerberos cache exists, but later SAMR operations may still fail. There is no explicit cleanup for `RemoteOperations` connections. The printed key format strips the first two characters from `key`, assuming a fixed prefix.

## Test Signals

Tests should mock `KeyListSecrets` to verify partial/full TGT/key call sequencing, LIST parsing, required option validation, domain derivation from `-kdc`, and all-user filtering. Integration tests need an RODC lab and should compare extracted keys for allowed users, denied built-in users, full enumeration, and explicit target-file mode.
