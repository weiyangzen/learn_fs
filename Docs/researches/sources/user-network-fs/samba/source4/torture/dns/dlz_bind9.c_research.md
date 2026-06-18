# sources/user-network-fs/samba/source4/torture/dns/dlz_bind9.c Research

## Purpose
This file defines the `dlz_bind9` smbtorture suite for Samba AD DC DNS integration through the BIND9 DLZ module. It validates module creation, BIND callback registration, zone configuration, GENSEC based update authorization, record lookup and dump callbacks, dynamic update transactions, zone transfer authorization, and DNS aging timestamp behavior backed by the AD DNS LDB.

## Important APIs, Types, And Functions
The suite calls the DLZ entry points from `dns_server/dlz_minimal.h`: `dlz_version`, `dlz_create`, `dlz_configure`, `dlz_destroy`, `dlz_lookup`, `dlz_allnodes`, `dlz_newversion`, `dlz_addrdataset`, `dlz_subrdataset`, `dlz_delrdataset`, `dlz_closeversion`, `dlz_ssumatch`, and `dlz_allowzonexfr`. `dlz_bind9_binddns_dir()` builds the `ldb://.../dns/sam.ldb` URL from `lpcfg_binddns_dir()`. `dlz_bind9_log_wrapper()` adapts DLZ logging to `torture_comment()` via the global `tctx_static`. `dlz_bind9_writeable_zone_hook()` opens `dns/sam.ldb` with `samdb_connect_url()` and verifies a `dnsZone` object exists. `test_expected_record` and `test_expected_rr` hold expected callback output; `dlz_bind9_putrr_hook()` and `dlz_bind9_putnamedrr_hook()` feed actual records into the shared comparison helper.

## Control Flow
The tests commonly create a DLZ instance with `-H ldb://.../dns/sam.ldb`, register callbacks, configure it, run one operation, then destroy `dbdata`. Basic tests check version, create, configure, repeated configure, and destroy order. Security tests build a GENSEC client for the `dns/host.domain` service, generate an initial token, and pass it to `dlz_ssumatch()`. Lookup and zone dump tests assert callback output for SOA, NS, A, AAAA, and SRV records.

`test_dlz_bind9_update01()` authenticates update rights, opens DLZ versions, adds and removes A records, commits or cancels transactions, and checks lookup results after each step. `test_dlz_bind9_allowzonexfr()` checks default denial, then mutates `lp_ctx` allow/deny client lists. `test_dlz_bind9_aging()` adds several record types, inspects `dnsRecord` blobs through NDR, toggles zone aging via `samba-tool dns zoneoptions`, directly edits record timestamps in LDB, and validates refresh/static timestamp semantics.

## State And Persistence
Several tests mutate persistent AD DNS state. `update01` creates and deletes a DNS node named after the test function. `aging` creates records under `CN=MicrosoftDNS,DC=DomainDnsZones`, changes zone aging options, and writes `dnsRecord` blobs with `ldb_modify()`. Failures before cleanup can leave DNS nodes or zone aging changes behind. `calls_zone_hook` and `tctx_static` are process-global state and make same-process parallel execution risky.

## Dependencies And Integration Points
The file depends on smbtorture, BIND DLZ shim APIs, GENSEC, command line credentials, LDB/SamDB, DSDB DNS utilities, generated DNS NDR types, and runtime AD DC settings such as `host`, `dnsdomain`, `SERVER`, `USERNAME`, and `PASSWORD`. `wscript_build` compiles it as `TORTURE_BIND_DNS` for AD DC builds with `-DBIND_VERSION_9_16`.

## Risks And Test Signals
Signals are exact ISC result codes, callback invocation counts, normalized DNS data comparisons, NDR timestamp checks, and zone transfer authorization results. Risks include reliance on a live AD DC, mutable global state, shelling out to `samba-tool`, time-sensitive aging checks, persistent LDB mutations on assertion failure, and BIND API version coupling.
