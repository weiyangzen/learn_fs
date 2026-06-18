# sources/user-network-fs/samba/source4/torture/libnet/libnet_lookup.c

## Purpose
`libnet_lookup.c` checks libnet name and DC discovery helpers: generic NetBIOS lookup, host lookup, PDC/DC enumeration, and SAM account-name lookup.

## Important APIs, types, and functions
Entry points are `torture_lookup()`, `torture_lookup_host()`, `torture_lookup_pdc()`, and `torture_lookup_sam_name()`. They exercise `libnet_Lookup`, `libnet_LookupHost`, `libnet_LookupDCs`, and `libnet_LookupName` using `libnet_context`, `libnet_Lookup`, `libnet_LookupDCs`, and `libnet_LookupName` request structures.

## Control flow
Each test creates a libnet context, attaches command-line credentials, and chooses the host from `torture:host` or an RPC binding. Name lookup requests are then issued synchronously. The PDC test uses the workgroup as the domain and `NBT_NAME_PDC`; the SAM-name test resolves the hard-coded `Administrator` account in the configured domain.

## State and persistence behavior
These are discovery-only tests. They allocate temporary talloc state and may use resolver or network caches, but they do not change remote directory or file state.

## Dependencies and integration points
The file integrates with Samba resolver context behavior through libnet, with `torture_rpc_binding()` for host fallback, and with loadparm workgroup settings. It also relies on a conventional `Administrator` account existing for `libnet_LookupName`.

## Risks and edge cases
Tests are sensitive to NetBIOS/DNS configuration, domain naming, and whether the test environment exposes PDC records. Hard-coding `Administrator` can fail in unusual domains where the account is renamed, hidden, or inaccessible to the test credentials.

## Test signals
Passing tests indicate that libnet can resolve host addresses, discover PDC/DC candidates, and resolve an account name to SAM identity data using the configured credentials and domain context.
