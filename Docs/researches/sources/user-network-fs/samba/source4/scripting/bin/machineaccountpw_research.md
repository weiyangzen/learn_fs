<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/machineaccountpw -->
# sources/user-network-fs/samba/source4/scripting/bin/machineaccountpw

## Purpose

`machineaccountpw` prints the local machine account password from Samba stored credentials.

## Important APIs, Types, and Functions

It uses Samba options, `Credentials()`, `creds.guess()`, `creds.set_machine_account()`, `creds.get_password()`, and catches `RuntimeError` and `NTSTATUSError` for friendlier failures.

## Control Flow

The script accepts no positional arguments. It loads smb.conf, initializes credentials, selects the machine account, and prints the password. Missing configuration or stored credentials exits with diagnostic output.

## State and Persistence Behavior

It reads stored machine account secrets and writes the plaintext password to stdout. It does not modify credentials.

## Dependencies and Integration Points

It depends on Samba Python credentials and local Samba private secrets.

## Risks and Edge Cases

The primary risk is plaintext secret disclosure to stdout, shell history capture, or logs. The script intentionally exposes sensitive material for automation.

## Test Signals

Tests should cover no-argument validation, missing smb.conf, missing machine account, successful password output, and ensuring errors go to stderr with nonzero exits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/machineaccountpw -->
