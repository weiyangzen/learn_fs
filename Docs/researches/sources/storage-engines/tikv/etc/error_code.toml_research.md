# sources/storage-engines/tikv/etc/error_code.toml

## Purpose
Registers stable TiKV error-code identifiers grouped by subsystem. The file maps namespaced keys such as `KV:Storage:WriteConflict` to matching string payloads used by error-code generation and diagnostics.

## Important APIs, Types, and Functions
Sections cover Cloud, Codec, Coprocessor, Encryption, Engine, PD, Raft, Raftstore, SST importer, and Storage errors. Each table contains an `error` multiline string mirroring the table key, providing a canonical textual identifier.

## Control Flow
Declarative TOML is parsed by TiKV build or tooling code that generates/validates error-code definitions. There is no branching in the file; ordering primarily aids maintainability and review.

## State and Persistence Behavior
The identifiers are persistent compatibility surface for logs, metrics, clients, support tooling, and documentation. Renaming or deleting entries can break alerting, dashboards, client matching, or generated code that expects stable codes.

## Dependencies and Integration Points
Integrated with TiKV error handling, generated error-code modules, telemetry/logging, and external tooling that classifies errors by subsystem and reason.

## Risks
Duplication between table name and `error` value can drift. Typos become stable public identifiers if not caught early. Missing entries for new errors can force generic `Unknown` handling and reduce observability.

## Test Signals
Run the repository's error-code generation/validation checks after edits. Add tests that every error table value equals its key and that Rust error enums reference registered codes. Review alert/log dashboards when introducing new high-level classes.
