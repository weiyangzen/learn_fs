# sources/user-network-fs/impacket/examples/samedit.py

## Purpose

`samedit.py` edits an offline SAM hive in place to replace an existing local user's password hash. It uses a SYSTEM hive or explicit bootkey to decrypt/encrypt SAM password material and either derives an NT hash from a password or accepts supplied hashes.

## Important APIs, Types, and Functions

This script has no custom classes. It uses `LocalOperations.getBootKey()` from `impacket.examples.secretsdump`, `SAMHashes.edit()`/`finish()`, and `ntlm.NTOWFv1()`. CLI validation enforces exactly one bootkey source and exactly one password/hash source.

## Control Flow

The CLI requires user and SAM hive paths plus either `-system` or `-bootkey`, and either `-password` or `-hashes`. It initializes logging, validates mutually exclusive options, obtains the bootkey, constructs `SAMHashes(options.sam, bootkey, False)`, converts the desired credential material to LM/NT hash bytes, calls `hive.edit(user, NTHash, LMHash)`, logs errors, and always calls `hive.finish()`.

## State and Persistence Behavior

The SAM hive file is modified in place. No backup is created by this script. The SYSTEM hive is read-only when supplied. Password/hash data exists in memory during the run and may be visible in shell history if passed as arguments.

## Dependencies and Integration Points

It depends on Impacket `ntlm`, `LocalOperations`, `SAMHashes`, and the example logger. It integrates with offline Windows SAM/SYSTEM hive formats rather than remote services.

## Risks and Edge Cases

The tool only replaces an existing user's password and does not create users. In-place editing can corrupt a hive if interrupted or if the wrong bootkey is supplied. Hash parsing accepts a single NT hash or `LM:NT` pair but does not validate lengths before unhexlify/use. `logger.init(options.ts)` ignores the debug flag until logging level is manually set.

## Test Signals

Tests should use disposable SAM/SYSTEM fixtures to verify password-derived hash editing, direct NT hash editing, LM:NT hash editing, invalid option combinations, invalid hex handling, missing user behavior, and that `finish()` is invoked on edit failure.
