# sources/storage-engines/foundationdb/fdbcli/IdempotencyIdsCommand.cpp

Purpose: Implements `idempotencyids`, exposing status for idempotency-id metadata and a cleanup action for reclaiming space used by old idempotency IDs.

Important APIs/types/functions: `idempotencyIdsCommandActor(Database, tokens)`, private `parseAgeValue`, `getIdmpKeyStatus`, `cleanIdempotencyIds`, `JsonBuilderObject`, and command registration `idempotencyIdsCommandFactory`.

Control flow: The actor requires two or three tokens. `status` requires no additional argument, awaits `getIdmpKeyStatus`, and prints JSON. `clear <min_age_seconds>` parses the age using `std::stod`, rejects parse failures, calls `cleanIdempotencyIds`, and prints success. Unknown actions or wrong arity print usage and return false.

State and persistence behavior: `status` is read-only; `clear` mutates idempotency ID metadata through fdbclient helpers and can expire transaction versions older than the specified age. No local state is persisted.

Dependencies and integration points: Depends on fdbclient `IdempotencyId` helpers, JSON builder, fdbcli parsing/help, and cluster idempotency metadata.

Risks: `std::stod` accepts some partial strings unless position is checked; `parseAgeValue` does not validate full-token consumption, finite values, or non-negative ages. Cleanup has potentially broad historical transaction-version effects, so input validation matters.

Test signals: Cover status JSON, valid clear, invalid age, partial numeric age, negative/NaN/infinite age behavior, wrong arity, unknown actions, and helper error propagation.
