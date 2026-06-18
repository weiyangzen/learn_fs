<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.h

## Purpose
This header declares the Kerberos utility API used by gssd upcall processing and daemon shutdown. It also hides selected MIT versus Heimdal cleanup differences behind macros.

## APIs And Types
Public functions cover user ccache setup, machine credential list allocation/free, principal destruction, machine credential refresh, Kerberos error strings, default realm lookup, direct user credential acquisition, bad service credential removal, and enctype list formatting. When allowable-enctype support is configured, it also declares `limit_krb5_enctypes`, `get_allowed_enctypes`, and `get_krb5_library_permitted_enctypes`. Compatibility macros map name, realm, and keytab-entry freeing to MIT or Heimdal APIs.

## State, Dependencies, And Integration
The header depends on `krb5.h`, either libtirpc `auth_gss.h` or local OIDs, and compile-time Kerberos feature macros. It is included by `gssd.c` startup and `gssd_proc.c` upcall handling.

## Risks And Test Signals
Risks include compile-time API differences between MIT and Heimdal, optional function declarations only under configure probes, and ownership expectations for returned strings/lists. Test both Kerberos implementations, allowable-enctype enabled/disabled builds, and callers freeing all returned allocations correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.h -->
