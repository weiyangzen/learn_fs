# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCConfig.hh

## Purpose

`XrdOfsTPCConfig.hh` defines the configuration structure shared by TPC authorization, validation, and transfer-program execution. It centralizes defaults and flags for the OFS TPC subsystem.

## Important APIs, Types, and Functions

The exported type is `struct XrdOfsTPCConfig`. Fields include monitor pointer `tpcMon`, transfer program `XfrProg`, checksum type `cksType`, credential path `cPath`, reproxy path format `rPath`, TTLs `maxTTL`/`dflTTL`, stream defaults and maxes, concurrent transfer max `xfrMax`, error monitor level `errMon`, and booleans `LogOK`, `doEcho`, `autoRM`, `noids`, and `fCreds`.

## Control Flow

There is no executable control flow beyond the constructor. Runtime flow reads this struct from `XrdOfsTPC`, `XrdOfsTPCAuth`, `XrdOfsTPCInfo`, and `XrdOfsTPCProg` to decide authorization lifetime, transfer command setup, stream count, logging, monitoring, credential export, and cleanup.

## State and Persistence Behavior

The configuration is a process-lifetime object in `XrdOfsTPCParms::Cfg`. It stores owned or borrowed C strings allocated by the surrounding configuration parser; the destructor intentionally does nothing because the global is never deleted.

## Dependencies and Integration Points

It forward-declares `XrdXrootdTpcMon` and otherwise stays standalone. It is the integration point between xrootd config parsing and the TPC runtime files in this subset.

## Risks and Edge Cases

Defaults are behaviorally significant: `maxTTL=15`, `dflTTL=7`, `xfrMax=9`, and `noids=true` affect security and concurrency even when config is sparse. Because string ownership is not documented by the struct itself, config-parser changes must preserve lifetime assumptions.

## Test Signals

Configuration tests should verify default transfer behavior, TTL clamping, stream clamping, monitor activation, `autoRM`, `fCreds`, and reproxy format expansion.
