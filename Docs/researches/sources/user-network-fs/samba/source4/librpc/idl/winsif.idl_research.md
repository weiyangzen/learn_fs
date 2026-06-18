# sources/user-network-fs/samba/source4/librpc/idl/winsif.idl

## Purpose

`winsif.idl` defines the WINS Administration Interface RPC contract. It models record actions, status/config/statistics queries, replication triggers, scavenging, backup, database range operations, browser-name retrieval, flags, and worker-thread updates.

## Important APIs And Types

The interface UUID is `45f52c28-7f9f-101a-b52b-08002b2efabe`, version 1.0, imports NBT IDL, and uses the NBT helper header. Core types include `winsif_Address`, `winsif_Action`, `winsif_RecordType`, `winsif_NodeType`, `winsif_RecordState`, and `winsif_RecordAction`. `winsif_RecordAction` carries command, optional NBT name, name length, record type, address arrays, version, node type, owner, state, static flag, and expiry.

Status types include address/version maps, replication counters, statistics counters, timestamps, `winsif_Stat`, old fixed-size `winsif_Results`, and newer dynamic `winsif_ResultsNew`. RPC calls span function numbers 0x00 through 0x15, including `winsif_WinsRecordAction`, `winsif_WinsStatus`, `winsif_WinsTrigger`, `winsif_WinsDoStaticInit`, `winsif_WinsDoScavenging`, `winsif_WinsGetDbRecs`, `winsif_WinsTerm`, `winsif_WinsBackup`, `winsif_WinsDelDbRecs`, `winsif_WinsPullRange`, `winsif_WinsSetPriorityClass`, `winsif_WinsResetCounters`, `winsif_WinsWorkerThreadUpdate`, `winsif_WinsGetNameAndAdd`, browser-name calls, `winsif_WinsGetDbRecsByName`, `winsif_WinsStatusWHdl`, and `winsif_WinsDoScanvengingNew`.

## Control Flow And State

The file defines wire layout only. Operationally the calls mutate WINS database records, trigger replication, delete ranges, adjust service priority/threads/flags, run scavenging, and terminate or back up the service. Several calls use `[in,out,ref]` records or results, so server code can update caller-provided structures.

## Dependencies And Integration Points

It integrates with generated NDR code, NBT name types (`wrepl_nbt_name`), WINS replication structures, and WINS service/admin implementations. DOS and UTF16 charset annotations indicate compatibility with legacy Windows admin protocols.

## Risks

This interface exposes powerful administrative state changes. Counted arrays and optional name pointers must be validated carefully. The old `winsif_Results` uses a fixed 25-entry map, while `winsif_ResultsNew` is dynamic; server/client mismatch can truncate status. The function name `WinsDoScanvengingNew` appears misspelled but is part of the IDL contract and should not be casually renamed.

## Test Signals

IDL generation, NDR round trips for records/status results, and interoperability tests against known WINS admin clients are key. Runtime tests should cover insert/query/delete/release actions, static init path encoding, range retrieval, browser names, scavenging requests, and malformed counted arrays.
