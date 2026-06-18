# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumHelper.hh

## Purpose

`CheckSumHelper` is a convenience wrapper around `XrdCksCalc` calculators for streaming checksum calculation in copy, stdio, ZIP, and error-correction paths. It hides calculator lookup through `DefaultEnv::GetCheckSumManager`, incremental updates, final formatting through `XrdCksData`, and raw final value extraction.

## Important APIs, types, and functions

The constructor stores a display name and checksum type. `Initialize()` is a no-op for an empty checksum type; otherwise it obtains the global `CheckSumManager`, requests a calculator for `pCkSumType`, logs failures, and stores the returned calculator in `pCksCalcObj`.

`Update(const void*, uint32_t)` feeds bytes into the calculator when one exists. `GetCheckSum(std::string&, std::string&)` finalizes the calculator, formats the digest as `<type>:<normalized-value>`, logs it, and returns an `XRootDStatus`. `GetRawCheckSum<T>` finalizes and reinterprets the raw digest as `T`, after verifying that `sizeof(T)` matches the calculator's final size. `GetType()` returns the configured checksum type.

`GetCheckSumImpl` is the shared private sanity check. It verifies initialization, asks the calculator for its actual type and output size, and rejects type mismatches.

## Control flow

Users construct a helper, call `Initialize`, feed every data block with `Update`, then call `GetCheckSum` or `GetRawCheckSum`. In `ClassicCopyJob`, local-file and stdio sources/destinations update helpers during streaming; remote checksum requests bypass local helpers and ask the remote server through `Utils::GetRemoteCheckSum`.

## State and persistence behavior

The helper owns one `XrdCksCalc*` and deletes it in the destructor. It keeps only transient checksum state. There is no persistence. Calling finalization methods before `Initialize` returns `errCheckSumError`; calling them after partial updates finalizes whatever bytes were seen.

## Dependencies and integration points

Dependencies include `XrdClXRootDResponses`, `XrdClConstants`, `XrdCksCalc`, `XrdClCheckSumManager`, `XrdClLog`, and `XrdClUtils`. Integration points include `ClassicCopyJob`, `XrdClEcHandler`, `Utils::NormalizeChecksum`, and `DefaultEnv` for logging and checksum manager access.

## Risks and edge cases

`GetCheckSum` allocates a fixed 265-byte buffer and asks `XrdCksData::Get` for 256 bytes; this assumes all supported checksum string encodings fit. `GetRawCheckSum` uses `reinterpret_cast<T*>` on the calculator's final buffer, which can carry alignment and endian assumptions; current ZIP CRC32 use is the intended case.

`Initialize` does not delete an existing calculator before replacing it, so repeated initialization on one helper would leak. The helper is not thread-safe and should be confined to one transfer stream. `GetAddCks` call sites need to avoid adding their own type prefix twice; behavior differs between stdin and regular source helpers in this work item.

## Test signals

No focused helper tests are present. Indirect signals come from `xrdcp` checksum modes, ZIP append CRC metadata, `XrdClEcHandler` page checksum validation, and local checksum behavior in `Utils`. Useful tests would include empty type no-op, missing calculator, type mismatch, raw checksum size mismatch, repeated initialization, and normalized output for each built-in algorithm.
