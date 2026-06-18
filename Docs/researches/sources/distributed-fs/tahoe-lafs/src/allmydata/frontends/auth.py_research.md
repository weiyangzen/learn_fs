# sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/auth.py

## Purpose

This module implements account-file authentication support for frontends, currently centered on SSH public-key credentials for SFTP users mapped to Tahoe root caps.

## Important APIs, Types, And Functions

`NeedRootcapLookupScheme` signals missing account lookup configuration. `FTPAvatarID` stores username and rootcap. `AccountFileChecker` implements Twisted `ICredentialsChecker` for `ISSHPrivateKey`, loads account maps, and delegates key validation to `SSHPublicKeyChecker`. Helper functions are `open_account_file()`, `load_account_file()`, `content_lines()`, `parse_accounts()`, and `create_account_maps()`.

## Control Flow

`AccountFileChecker` expands and opens the account file at construction, parses non-empty non-comment lines, rejects password-based entries, builds username-to-rootcap and username-to-key maps, and creates an in-memory SSH key checker. During authentication, `requestAvatarId()` validates SSH private-key credentials and maps the resulting username to an `FTPAvatarID`.

## State And Persistence

Persistent state is the account file. Runtime state is `rootcaps`, public-key maps, and the Twisted key checker. There is no reload logic after construction.

## Dependencies And Integration Points

It depends on Twisted cred/conch checkers, SSH key parsing, Tahoe `BytesKeyDict`, and path expansion. `frontends.sftpd.SFTPServer` uses `AccountFileChecker` to authenticate users and supply root caps to the SFTP dispatcher.

## Risks

Password-based accounts are explicitly unsupported. Account files are loaded only once, so changes require service restart. `parse_accounts()` uses whitespace splitting and assumes the final field is the rootcap; malformed lines raise. Duplicate names overwrite prior rootcaps/pubkeys in the maps. Rootcaps are encoded as UTF-8 bytes and later passed to node creation.

## Test Signals

Parse comments/blanks, valid SSH public-key account lines, password rejection, malformed line errors, duplicate-name behavior, credential success/failure through `SSHPublicKeyChecker`, and SFTP integration mapping username to rootcap.
