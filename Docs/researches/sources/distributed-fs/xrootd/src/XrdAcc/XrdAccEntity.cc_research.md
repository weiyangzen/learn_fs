# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.cc

## Purpose

`XrdAccEntity.cc` compiles authorization-relevant attributes from `XrdSecEntity` into reusable `XrdAccEntity` objects. It tokenizes virtual organization, role, and group strings into aligned attribute combinations and caches the result on the security entity. The file was read completely.

## Important APIs, Types, and Functions

The constructor copies `secP->vorg`, `role`, and `grps`, then builds `attrVec`. `GetEntity()` retrieves cached attributes from `secP->eaAPI` using a static signature or builds a new object. `PutEntity()` attaches a newly built object to the entity or deletes it if another thread won. `OneOrZero()` accepts the short-form case with zero or one VO/role. `setAttr()` advances tokenizers for aligned multi-attribute columns. `setError()` stores a diagnostic destination.

## Control Flow

When access checks start, `XrdAccEntityInit` calls `GetEntity()`. If attributes are already cached, they are reused. If not, a new object tokenizes attributes. The common case of at most one VO and role combines that with each group token. The multi-column case advances VO, role, and group lists together and fails if one list ends early. `XrdAccEntityInit` attaches newly built objects on destruction.

## State and Persistence Behavior

Each entity object owns duplicated source strings and a vector of lightweight `EntityAttr` entries pointing into those strings. Cached objects persist on `XrdSecEntity` via `eaAPI`. `accSig` is a static key for the attribute cache, and `eDest` is a file-local static error pointer.

## Dependencies and Integration Points

It depends on `XrdSecEntity`, `XrdSecEntityAttr`, `XrdSecAttr`, `XrdOucTokenizer`, and `XrdSysError`. `XrdAccAccess` iterates the resulting attributes through `Next()`.

## Risks and Edge Cases

The multi-column mode requires all provided lists to have the same number of tokens; mismatches deny compiled-entity creation and can deny access. Pointers in `attrVec` are valid only while duplicated strings live. Parallel caching relies on `eaAPI->Add()` rejecting duplicates. Tokenization treats spaces as separators after any configured higher-level substitutions.

## Test Signals

Tests should cover no attributes, single VO/role with multiple groups, aligned multi-column VO/role/group lists, mismatched list lengths, cache reuse, parallel creation, and diagnostic emission on invalid attributes.
