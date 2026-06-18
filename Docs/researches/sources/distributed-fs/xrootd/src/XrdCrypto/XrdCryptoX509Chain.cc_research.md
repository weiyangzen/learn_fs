# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.cc

## Purpose

`XrdCryptoX509Chain.cc` implements a lightweight singly linked list of `XrdCryptoX509` certificates plus generic chain ordering, CA discovery, validity checking, and signature verification.

## Important APIs and Functions

Constructors initialize empty or single-certificate chains and copy chain node topology without copying certificates. `Cleanup()` deletes nodes and optionally certificate objects. `CheckCA()` finds a valid CA, verifies self-signature unless configured otherwise, moves it to the front, and records CA name/hash/status. `PutInFront()`, `InsertAfter()`, `PushBack()`, and `Remove()` mutate list topology. `SearchByIssuer()`/`SearchBySubject()` and their private finders support exact, prefix, and suffix modes. `Reorder()` arranges certificates so each node signs the next. `Verify()` reorders, checks path depth, validates a CA, then verifies each subsequent certificate against the previous signer. Internal `Verify()` enforces presence, type, CRL revocation if supplied, time validity, and signature verification. `CAname()`, `EECname()`, `CAhash()`, and `EEChash()` lazily derive cached names.

## Control Flow

Generic verification starts by reordering the chain, interpreting `x509ChainVerifyOpt_t` options, checking path depth, finding/verifying the CA, then walking signer/certificate pairs from top to bottom. `Reorder()` first finds a top-most certificate whose issuer is not present, moves it to the front, then repeatedly finds children whose issuer matches the current subject.

## State and Persistence Behavior

The chain owns nodes but not necessarily certificates unless `Cleanup()` is called. It caches iterator state (`current`, `previous`), endpoints (`begin`, `end`), effective CA, size, last error text, CA/EEC names and hashes, and CA status. Copy construction shares certificate pointers, so ownership must be external or carefully managed.

## Dependencies and Integration Points

It depends on `XrdCryptoX509`, `XrdCryptoX509Crl`, `XrdSutBucket`, `XrdOucString`, and crypto trace macros. `XrdCryptogsiX509Chain` subclasses it to enforce GSI proxy rules.

## Risks and Edge Cases

`InsertAfter()` does not unlink an existing node before inserting it after a new parent, so moving existing certificates can corrupt list topology. `PushBack()` deletes duplicate certificate pointers passed by caller, creating surprising ownership behavior. Suffix matching computes `strlen(pi) - strlen(issuer)` without guarding negative values. Generic `Verify()` sets a path-depth error but does not immediately return, so later checks can overwrite or ignore it. Iterator state makes concurrent iteration unsafe.

## Test Signals

Tests should cover unordered chains, sub-CA chains, duplicate insertion, remove while iterating, absent/invalid CA, CRL revocation, expired certs, path depth failures, prefix/suffix searches with short strings, and copy/cleanup ownership scenarios.
