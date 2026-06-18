# sources/user-network-fs/samba/source4/torture/ldap/cldapbench.c

## Purpose

`cldapbench.c` is a CLDAP benchmark torture test. It measures how quickly a target can answer parallel netlogon pings and RootDSE CLDAP searches over a configurable time window.

## Important APIs, Types, and Functions

- `struct bench_state` tracks pass/fail counters.
- `request_netlogon_handler()` receives asynchronous `netlogon_pings_send()` completions.
- `bench_cldap_netlogon()` maintains up to 10 outstanding netlogon ping requests and reports queries per second.
- `request_rootdse_handler()` receives asynchronous `cldap_search_send()` completions.
- `bench_cldap_rootdse()` runs the same windowed benchmark for RootDSE CLDAP searches.
- `torture_bench_cldap()` resolves the target and runs both benchmarks.

## Control Flow

The test resolves the configured host to an IP. Each benchmark records a start time and, until `torture:timelimit` expires, keeps no more than 10 requests outstanding. It drives completions with `tevent_loop_once()`, then drains remaining requests and prints pass-rate and failure count. Netlogon uses `netlogon_pings_send()` with `ntversion=6`; RootDSE uses `cldap_search_send()` with `(objectClass=*)`.

## State and Persistence Behavior

No directory state is changed. Runtime state is only outstanding tevent requests, counters, and the CLDAP socket for RootDSE.

## Dependencies and Integration Points

The benchmark depends on tevent, `netlogon_ping` helpers, CLDAP client APIs, name resolution, `tsocket`, loadparm `client netlogon ping protocol`, and torture settings `timelimit` and `progress`. It is registered as `ldap.bench-cldap`.

## Risks and Edge Cases

It is performance-oriented and not a strict correctness test; it always returns true even with failures counted. Network latency, UDP drops, resolver choice, and event loop behavior affect results. The fixed window of 10 outstanding requests may not stress all servers equally.

## Test Signals

Useful signals are the printed queries-per-second rate and failure count for netlogon and RootDSE. A sharp increase in failures or severe rate regression indicates CLDAP/server/network problems.
