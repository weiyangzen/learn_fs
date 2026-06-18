# sources/user-network-fs/samba/source3/libnet/libnet_dssync_keytab.c

## Purpose

Implements a DSSync backend that writes replicated account and trust secrets to a keytab. It also stores UTDV state and selected metadata as synthetic keytab entries to support incremental or sparse replication.

## Important APIs, Types, and Functions

Exports `libnet_dssync_keytab_ops` with `keytab_startup`, `keytab_process_objects`, and `keytab_finish`. Important parsers are `parse_supplemental_credentials`, `parse_user`, `parse_tdo`, `parse_trustAuthInOutBlob`, and `parse_AuthenticationInformation`. `store_or_fetch_attribute` persists or recovers metadata entries. Non-ADS builds return `NT_STATUS_NOT_SUPPORTED`.

## Control Flow

Startup opens the keytab, sets realm/cleanup options, and searches for `UTDV/<nc_dn>@<realm>` to recover the old vector. Object processing filters deleted/recycled objects, routes password/supplemental credentials to user parsing, and trust auth attributes to trust parsing. User parsing emits RC4 keys from NT hashes, AES/other keys from Primary:Kerberos v3/v4 supplemental credentials, and history keys by kvno. Trust parsing derives incoming/outgoing krbtgt salts and emits current/previous trust keys. Finish serializes the new UTDV and calls `libnet_keytab_add`.

## State and Persistence Behavior

Persistent state is the target keytab. It can contain real principals, trust principals, UTDV blobs, and metadata entries such as `sAMAccountName/<dn>@<realm>` and `REMOTETRUSTNAME/<dn>@<realm>`. `clean_old_entries` removes older matching principals/enctypes during final write.

## Dependencies and Integration Points

Depends on Kerberos, `libnet_keytab`, generated DRS blob parsers, MD4 for NT hashes from clear trust passwords, and decrypted DRS attributes supplied by `libnet_dssync.c`.

## Risks and Test Signals

Risks include persistence of sensitive secrets, kvno underflow for old keys, stale synthetic metadata reuse, and logged-but-continued trust parse failures. Tests should cover UTDV round-trip, Kerberos v3/v4 credentials, password history, trust incoming/outgoing auth arrays, object filtering, deleted objects, and non-ADS behavior.
