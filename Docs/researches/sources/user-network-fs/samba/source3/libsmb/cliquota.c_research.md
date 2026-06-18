# sources/user-network-fs/samba/source3/libsmb/cliquota.c

## Purpose

This file implements SMB client quota support for user quotas and filesystem default quota data. It can open the quota pseudo-file, parse and build NT quota records, list user quotas, and get/set per-user or filesystem quota state over SMB1 NT transact/Trans2 or SMB2 helper paths.

## Important APIs, Types, and Functions

Key APIs are `cli_get_quota_handle()`, `parse_user_quota_record()`, `parse_user_quota_list()`, `build_user_quota_buffer()`, `build_fs_quota_buffer()`, `cli_get_user_quota()`, `cli_set_user_quota()`, `cli_list_user_quota()`, `cli_get_fs_quota_info()`, `cli_set_fs_quota_info()`, and `fill_quota_buffer()`. `SMB_NTQUOTA_STRUCT` and `SMB_NTQUOTA_LIST` carry parsed quotas and list ownership.

## Control Flow

SMB1 user quota queries build NDR `nttrans_query_quota_params` and optional `file_get_quota_info`, call `SMBnttrans` with `NT_TRANSACT_GET_USER_QUOTA`, then parse `file_quota_information`. Listing repeatedly calls `cli_list_user_quota_step()` with restart on the first request until non-OK; `NT_STATUS_NO_MORE_ENTRIES` is normalized to success. Set operations serialize quota records with `fill_quota_buffer()` and send `NT_TRANSACT_SET_USER_QUOTA`. Filesystem quota get/set uses Trans2 `SMB_FS_QUOTA_INFORMATION`.

## State and Persistence Behavior

Set operations persist quota thresholds, hard limits, usage records, and quota flags on the remote filesystem. Locally, quota lists are talloc-owned via `mem_ctx`; `free_ntquota_list()` releases the root context stored on list entries.

## Dependencies and Integration Points

The file integrates with fake file name `FAKE_FILE_NAME_QUOTA_WIN32`, SMB2 quota helpers, NDR quota/security generated code, overflow helpers, and `cli_trans`. It is used by administrative client paths that inspect or modify NT quota state.

## Risks and Test Signals

Risks include malformed NDR records, `next_entry_offset` loops or overruns, max-data truncation in `fill_quota_buffer()`, SMB1/SMB2 behavioral differences, and inconsistent ownership of list memory. Tests should cover single and multi-record quotas, offset zero termination, offset beyond buffer, max-data cutoffs, empty list behavior, SMB2 delegation, and fs quota buffers shorter than 48 bytes.
