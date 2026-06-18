<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics/value_retrieval_profile.go -->
## sources/storage-engines/pebble/metrics/value_retrieval_profile.go

Purpose: exposes a metric/profile type for separated value retrievals.

Important APIs and types: `ValueRetrievalProfile` is a type alias to `bytesprofile.Profile`, making the internal profile type available under the public metrics package namespace.

Control flow: none; this is a compile-time alias.

State and persistence: profile state is owned by `bytesprofile.Profile`; this file does not add state or persistence behavior.

Dependencies and integration: depends on `github.com/cockroachdb/pebble/internal/bytesprofile`. It is a public metrics integration point for code that reports or consumes separated value retrieval profiles without importing the internal package.

Risks and edge cases: as a type alias, API compatibility follows the internal profile type exactly. Changes to `bytesprofile.Profile` are exposed through this alias.

Test signals: no direct tests in the listed set.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics/value_retrieval_profile.go -->
