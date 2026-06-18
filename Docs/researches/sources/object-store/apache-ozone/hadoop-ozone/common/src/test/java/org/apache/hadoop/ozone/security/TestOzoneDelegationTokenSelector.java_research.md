# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSelector.java

Purpose: tests `OzoneDelegationTokenSelector` matching of delegation tokens by requested OM service.

Important APIs/types/functions: exercises `selectToken`, Hadoop `Token<OzoneTokenIdentifier>`, `OzoneTokenIdentifier.KIND_NAME`, `Text` service strings, and token `setService`.

Control flow and state: creates a token with service string `om1:9862,om2:9862,om3:9862`. Selecting for `om1:9862` returns the token. After changing token service to `om1:9863`, selecting `om1:9862` returns null and selecting `om1:9863` returns the token.

Dependencies and integration points: uses Hadoop security token APIs and random identifier/password bytes. This selector is used by clients choosing OM delegation tokens from UGI credentials.

Risks and test signals: catches service matching regressions for HA comma-separated service names and single-node services. It does not cover wrong token kind or multiple candidate ordering.
