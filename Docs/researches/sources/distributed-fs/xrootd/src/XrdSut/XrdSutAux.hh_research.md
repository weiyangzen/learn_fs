# sources/distributed-fs/xrootd/src/XrdSut/XrdSutAux.hh

## Purpose

This header defines XrdSut utility constants, bucket type identifiers, trace masks, general helper declarations, and the RAII file-lock helper class used by XRootD security utilities.

## Important APIs, types, and functions

Constants include buffer/print limits and the `kXRSBucketTypes` enum for serialized security exchange buckets such as crypto module, main buffer, seals, public key, cipher, random tag, user, host, credentials, messages, server/session ids, status, timestamps, certificates, algorithms, and AFS info. The header declares helper functions implemented in `XrdSutAux.cc`, optional external `XrdSutGetPass`, and `XrdSutFileLocker` with shared/exclusive lock modes.

## Control flow

The header only declares behavior. Consumers construct buckets and buffers using the enum values and call helpers for path/time/input/hex operations during security protocol setup and administration.

## State and persistence behavior

No state is stored in the header. The declared file-locker owns an advisory descriptor lock at runtime. Helper functions may inspect environment variables and user database state; `XrdSutMkdir` can create directories.

## Dependencies and integration points

The header depends on XRootD platform headers and protocol integer types. It forward-declares crypto factory, string, bucket, and buffer classes so security protocol code can use shared utility APIs with minimal includes.

## Risks and edge cases

The enum values are wire-format-visible in serialized XrdSut buffers; reordering or changing numeric values would break protocol compatibility. The default `XrdSutGetPass` is explicitly fallback-quality and can be replaced by defining `USE_EXTERNAL_GETPASS`. Several helper contracts rely on caller-allocated buffers of documented size.

## Test signals

Compatibility tests should assert bucket numeric values, especially `kXRS_cryptomod` and following values. Header consumers should compile with and without `USE_EXTERNAL_GETPASS`.
