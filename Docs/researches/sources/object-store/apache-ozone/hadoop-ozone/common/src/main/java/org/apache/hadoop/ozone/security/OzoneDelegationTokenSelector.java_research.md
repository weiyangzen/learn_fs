# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneDelegationTokenSelector.java

Purpose: Hadoop delegation token selector specialized for Ozone tokens.

Important APIs and types: Extends `AbstractDelegationTokenSelector<OzoneTokenIdentifier>` with `OzoneTokenIdentifier.KIND_NAME`. Overrides `selectToken` and uses `getSelectedTokens` to scan token collections.

Control flow: If the requested service is null it returns null. Otherwise it returns the first token whose kind is `OzoneToken` and whose service string contains the requested service string. Trace/debug logging records lookup and result.

State and persistence behavior: Stateless selector. It reads in-memory token collections; token persistence is handled by Hadoop credentials.

Dependencies and integration points: Referenced by `@TokenInfo` on `OzoneManagerProtocolPB` and used by secure OM clients when selecting credentials for RPC services.

Risks: Service matching uses substring containment rather than exact equality, which supports multi-address service strings but can accidentally match overlapping service names. The method uses an unchecked cast after kind filtering.

Test signals: Cover null service, empty tokens, exact and multi-address service matching, non-Ozone token rejection, first-match behavior, and overlapping service-name cases.
