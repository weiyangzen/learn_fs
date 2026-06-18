# sources/user-network-fs/samba/source4/torture/libnet/python/samr-test.py

## Purpose
This Python test verifies the Samba Python `net.SetPassword()` binding for a supplied account and new password.

## Important APIs, types, and functions
The `Libnet_SetPwdTest` class derives from `samba.tests.TestCase` and contains `test_SetPassword()`. It uses `self.get_credentials()` and `samba.net.Net.SetPassword` with `account_name`, the credential domain, the new password, and the current credentials.

## Control flow
At import time the script requires `ACCOUNT_NAME` and `NEW_PASS` environment variables. The test runner supplies credentials, then the single test calls `net.SetPassword()` and relies on exceptions to fail the case.

## State and persistence behavior
The test persistently changes the password of the named account. It does not restore the old password and is therefore intended for controlled accounts only.

## Dependencies and integration points
It integrates Samba's Python modules, `subunitrun`, and command-line credentials. The usage comment documents expected `PYTHONPATH`, `SUBUNITRUN`, and credential invocation.

## Risks and edge cases
Missing environment variables abort the module before tests run. Running against a real user account changes authentication state. Password policy, account lockout, insufficient rights, or mismatched credential domains can fail the test.

## Test signals
Success indicates that the Python libnet SAMR password-set path can authenticate with supplied credentials and update the target account password.
