# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/validation/TestVersionExtractor.java

## Purpose
This class tests `VersionExtractor`, which derives versioned validation inputs from either OM layout state or client request version and maps each extractor to its validator annotation class.

## Important APIs and Types
It uses `VersionExtractor.LAYOUT_VERSION_EXTRACTOR`, `VersionExtractor.CLIENT_VERSION_EXTRACTOR`, `OMLayoutFeature`, `OMLayoutVersionManager`, `ClientVersion`, `Versioned`, `ValidationContext`, `OMRequest`, `OMClientVersionValidator`, and `OMLayoutVersionValidator`.

## Control Flow and State
`testLayoutVersionExtractor` iterates every `OMLayoutFeature`, builds an `OMLayoutVersionManager` at that feature version, stubs the validation context's version manager, and expects the extractor to return the same layout feature. `testClientVersionExtractor` iterates all known `ClientVersion` enum values, stubs `OMRequest.getVersion()`, and expects exact enum recovery. `testClientVersionExtractorForFutureValues` passes versions greater than current and expects `ClientVersion.FUTURE_VERSION`. `testGetValidatorClass` asserts the enum-to-annotation mapping for both extractors.

## Dependencies and Integration Points
The class integrates OM layout feature versioning, request protobuf version fields, client-version fallback behavior, and annotation selection for runtime validation.

## Risks and Test Signals
Risks include off-by-one layout extraction, treating future clients as current/unknown values, or mapping an extractor to the wrong annotation class. Parameterized enum coverage and explicit future-version value tests provide the regression signals.
