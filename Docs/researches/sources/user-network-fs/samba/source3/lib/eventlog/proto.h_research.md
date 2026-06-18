# sources/user-network-fs/samba/source3/lib/eventlog/proto.h

Purpose: declares the eventlog utility API implemented by `eventlog.c`.

Important APIs/types/functions: declarations for TDB path/size/prune/close, text parsing, record fixup, record pull/push, TDB/EVT conversion, and full EVT export.

Control flow: callers use the prototypes to parse text event entries, mutate eventlog TDBs, and convert records for RPC/file output.

State/persistence behavior: functions declared here mutate TDB metadata/records and allocate returned structures on caller contexts.

Dependencies/integration: part of source3 internal prototype headers for eventlog RPC/service code.

Risks/test signals: signature drift or ownership misunderstanding breaks callers. Compile coverage and RPC eventlog tests are the primary signals.
