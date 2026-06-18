# sources/storage-engines/foundationdb/documentation/sphinx/source/api-common.rst.inc

## Purpose
Shared RST substitution library for FoundationDB API documentation. It centralizes cross-language text for API versioning, transactions, futures, atomic operations, options, tuple/subspace/directory layers, TLS/network options, locality APIs, and warnings.

## Important APIs, Types, and Functions
There is no executable API. Important substitutions include `|api-version|`, API-version rationale and multi-version warnings, transaction and commit-unknown-result blurbs, snapshot/read-your-writes text, atomic operation descriptions, watch behavior, conflict-range text, network/database/transaction option descriptions, future cancellation, `fdb.open`, subspace, directory, and locality blurbs.

## Control Flow
Sphinx expands substitutions in consuming language-specific documents. The file relies on local placeholders such as `|error-type|`, `|commit-func|`, and `|database-type|` being defined by each consuming page.

## State and Persistence Behavior
It stores documentation contracts only. The most state-like value is `|api-version| replace:: 800`. Behavioral text documents durable semantics for retries, watches, versionstamps, transaction options, conflict ranges, and atomic operations.

## Dependencies and Integration Points
Depends on Sphinx substitution/reference syntax and labels such as `multi-version-client-api`, `developer-guide-error-codes`, and `ACID`. It must stay synchronized with binding implementations, generated API references, and option definitions.

## Risks
Documentation drift can affect every language page that includes it. Missing placeholders in consuming pages produce broken docs. Version-specific API behavior must be reviewed whenever the documented API version changes.

## Test Signals
Run full Sphinx builds with warnings as errors, check unresolved substitutions and references, and review rendered option/error/API-version text against generated binding metadata and client headers.
