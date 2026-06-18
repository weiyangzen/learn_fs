# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/__init__.py

## Purpose

This package initializer documents the intended abstraction boundary for Tahoe-LAFS cryptography helpers.

## Important APIs, Types, And Functions

It defines no runtime symbols. The module docstring states that code inside Tahoe should use helper functions from `allmydata.crypto` modules instead of relying directly on `cryptography` object methods.

## Control Flow

Importing `allmydata.crypto` executes only the docstring.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

The package contains concrete helper modules for AES, Ed25519, RSA, shared errors, and prefix utilities.

## Risks

Because there are no re-exports, callers must import concrete submodules. Adding import-time crypto setup here would affect security-sensitive code globally.

## Test Signals

`import allmydata.crypto` should be side-effect free. Submodule tests cover actual behavior.
