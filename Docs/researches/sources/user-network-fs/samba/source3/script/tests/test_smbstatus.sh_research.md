# sources/user-network-fs/samba/source3/script/tests/test_smbstatus.sh

## Purpose
This test suite validates `smbstatus` plain, UID-resolved, sectioned, JSON, and JSON profile output while a real `smbclient` session holds an open file.

## Important APIs, Functions, and Control Flow
The script accepts server/IP/domain/user/password/userid/local path/prefix/client/status/config/protocol. Helpers create an smbclient command file that uploads and opens a file on `tmp`, runs `smbstatus` locally via `!UID_WRAPPER_INITIAL_RUID=0 UID_WRAPPER_INITIAL_EUID=0`, then closes and removes the file. `test_smbstatus` greps for numeric uid and `DENY_NONE`; `test_smbstatus_resolve_uids` is intended to check username output with `--resolve-uids`; `test_smbstatus_output` writes `--shares`, `--processes`, and `--locks` files; `test_smbstatus_json` validates JSON keys and selected fields with `jq`; `test_smbstatus_json_profile` validates profile JSON keys.

## State, Dependencies, Integration, and Risks
State is temporary command/status files under `$PREFIX` and a transient open remote file. Dependencies include `jq`, optional Jansson JSON support, uid_wrapper, exact `smbstatus` field names, and SMB signing/cipher output. The call labeled `resolve_uids` invokes `test_smbstatus` rather than `test_smbstatus_resolve_uids`, which appears to reduce coverage. Risks also include locale/output drift and cleanup after command failure. Test signals are absence of `NT_STATUS_`, grep checks, valid JSON parse, exact key lists, and expected field values.
