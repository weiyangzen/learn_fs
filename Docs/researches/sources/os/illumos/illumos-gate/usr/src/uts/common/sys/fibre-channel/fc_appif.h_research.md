# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_appif.h

## Purpose

`fc_appif.h` defines Fibre Channel application/transport-visible protocol structures: topology constants, CT headers, World Wide Names, service parameters, login payloads, name-server command buffers, RLS/RNID payloads, and NPIV creation entries.

## Main Types

`fc_ct_header_t` is a Common Transport header with endian-dependent bitfields for revision, initial node ID, FC service type/subtype, options, command/response, AIU size, reason/explanation, and vendor field.

`la_wwn_t` represents an 8-byte World Wide Name as raw bytes, two 32-bit words, or parsed NAA/nport/WWN fields.

`svc_param_t` and `com_svc_t` hold class/common service parameters.

`ls_code_t` stores an ELS code in endian-dependent layout.

`la_els_logi_t` is the ELS login payload with common service parameters, port/node WWNs, class 1-3 service parameters, reserved data, and vendor version.

`fc_ns_cmd_t` passes name-server commands with request/response payload pointers and a response CT header. 32-bit syscall variants exist under `_SYSCALL32`.

`fc_rls_acc_t`, `la_els_rls_t`, and `la_els_rls_acc_t` describe Read Link Status request/accept data.

`fc_rnid_t`, `la_els_rnid_t`, `fc_rnid_hdr_t`, and `la_els_rnid_acc_t` describe RNID node identification data.

`la_npiv_create_entry_t` describes an NPIV virtual port creation request with virtual node/port WWNs and vindex.

## Constants

Topology constants include unknown, private loop, public loop, fabric, point-to-point, and no-name-server states. `FC_IS_TOP_SWITCH()` identifies switched topologies.

Remote port states include invalid, valid/logged out, and logged in.

WWN, firmware revision, FCode revision, RNID data format, and RNID length constants are also defined.

## Research Notes

This header is part of the storage transport ABI. Its structures are used by Fibre Channel drivers and ioctl paths to exchange protocol records with transport and userland tooling. Endian-dependent bitfields are central to wire-format correctness.
