# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_Manifest

Purpose: Python helper that lists Rucio dataset contents in a simple line protocol for archive composition or inspection. Invocation is `XrdOssArc_Manifest ls <scope>:<dataset>`.

Important APIs/functions: `Decompose(dsn)` splits a Rucio DID into scope and name. `getClient()` constructs `DIDClient`. `do_LS()` calls `client.list_files(scope, did)` and prints each file as `scope:name`, followed by `===` as an end marker. `Main()` dispatches only the `ls` command.

State/persistence: no local persistence; all state comes from the Rucio catalog and stdout. Debug flag `XRDOSSARC_DEBUG` is parsed but not materially used beyond setting `Debug`.

Dependencies/integration: depends on `rucio.client.didclient.DIDClient` and is intended to be configured as a utility under XrdOssArc. Risks include `Decompose()` printing instead of calling `Emsg()` on invalid input, so malformed names may cause downstream unpacking errors; all Rucio exceptions are collapsed to `ENOENT` if text contains `not found` and `ECANCELED` otherwise. Test signals: valid listing order/content, invalid DID syntax, dataset not found, Rucio client construction failure, and `===` termination for consumers.
