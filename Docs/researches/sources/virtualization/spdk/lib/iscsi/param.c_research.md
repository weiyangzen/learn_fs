# File Research: sources/virtualization/spdk/lib/iscsi/param.c

Full-file read: 1199 lines.

This file implements iSCSI text parameter parsing, linked-list parameter storage, negotiation rules, and copying negotiated values into connection/session runtime fields.

Main responsibilities:
- Manage `struct iscsi_param` linked lists: add, delete, set, find, free, compare, and fetch values.
- Parse NUL-delimited `KEY=VAL` text buffers, including fragmented parameters across PDUs when the C bit is used.
- Initialize default connection and session parameter tables.
- Negotiate list, numeric min/max/declarative, boolean OR/AND, declarative, discovery, CHAP, extension, and unsupported keys.
- Enforce one-time negotiation state for most connection/session parameters.
- Copy negotiated values into `spdk_iscsi_conn` and `spdk_iscsi_sess`.

Important control flow:
- `iscsi_parse_param` validates key/value lengths, duplicates, `=`, and simple-value limits.
- `iscsi_parse_params` stitches a previous partial parameter to the current buffer, then optionally saves a new trailing partial when C bit is set.
- `iscsi_negotiate_params` checks discovery mode, ignores CHAP keys, handles `SendTargets` specially, reorders `FirstBurstLength` after `MaxBurstLength`, negotiates values, updates persistent params, and appends response text.
- `iscsi_special_param_construction` emits target-side declarative `MaxRecvDataSegmentLength` and fixes `FirstBurstLength <= MaxBurstLength`.
- `iscsi_copy_param2var` applies negotiated digest, burst, R2T, connection, and immediate-data values.

Integration points:
- Used by login/text handling in the iSCSI connection layer.
- Depends on constants and connection/session fields from `iscsi/iscsi.h` and `iscsi/conn.h`.
- Negotiation results influence later SCSI transfer sizing, digest behavior, and data-out/data-in sequencing.

Risks and review notes:
- The code mutates temporary comma-separated strings in place during list negotiation.
- Partial parameter handling is subtle and should be fuzzed with boundary-length buffers and C-bit splits.
- Numeric parsing uses `strtol` after parser validation but without full range revalidation in every path.
- Unknown non-extension keys produce `NotUnderstood`; `NotUnderstood` for understood keys is treated as login error.

Testing focus:
- C-bit fragmentation across every possible split position.
- Duplicate key rejection and max key/value lengths.
- Negotiation once-only errors.
- Discovery-session ignored parameters.
- `FirstBurstLength`/`MaxBurstLength` ordering and clamping.
