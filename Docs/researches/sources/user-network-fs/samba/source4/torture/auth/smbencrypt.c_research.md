# sources/user-network-fs/samba/source4/torture/auth/smbencrypt.c

## Purpose
This file provides a focused torture test for the legacy SMB DES password hash helper `E_deshash`. It checks known outputs and length behavior for LANMAN-style password hashing.

## Important APIs, Types, And Functions
The main test is `torture_deshash`; `torture_smbencrypt` registers it as `"deshash check"`. The tested API is `E_deshash` from `libcli/auth/libcli_auth.h`.

## Control Flow
The test iterates over hard-coded input strings, expected 16-byte hash outputs, and expected boolean return values. For each case it calls `E_deshash`, asserts that the boolean result matches, and compares the 16-byte output buffer regardless of pass/fail expectation.

## State And Persistence
All state is stack-local test data and result buffers. No persistent data is read or written.

## Dependencies And Integration Points
It integrates the torture framework with the low-level SMB authentication crypto helper. It is registered in the auth torture suite and protects compatibility for legacy hash calculations.

## Risks And Test Signals
Risks include reliance on legacy DES behavior, uppercase/truncation semantics in the underlying helper, and the subtle case where overlong input is expected to return false while leaving deterministic output. Passing this test signals stable empty-password, 8-byte, 13/14-byte, and overlong password hash behavior.
