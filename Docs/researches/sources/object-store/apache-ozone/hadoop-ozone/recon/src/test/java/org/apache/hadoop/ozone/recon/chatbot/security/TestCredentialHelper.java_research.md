# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/security/TestCredentialHelper.java

Purpose: This suite validates `CredentialHelper`, the chatbot secret resolver. It confirms secrets can be read from Hadoop credential provider JCEKS stores, plaintext configuration is used as fallback, missing values return an empty string/false availability, JCEKS values take priority over plaintext, and multiple chatbot provider keys can coexist in one credential store.

Important APIs/types/functions: The tests use `CredentialHelper.getSecret`, `hasSecret`, `OzoneConfiguration`, `CredentialProviderFactory.CREDENTIAL_PROVIDER_PATH`, `CredentialProvider.createCredentialEntry`, `flush`, JUnit `@TempDir`, and temporary JCEKS paths of the form `jceks://file...`.

Control flow: Each JCEKS test creates a temporary credential file path, sets it in the configuration, obtains a provider via Hadoop security APIs, writes one or more secret entries, flushes, and then constructs `CredentialHelper` to resolve them. Plaintext and missing-key tests use only config or empty config.

State and persistence behavior: Persistent state is the temporary JCEKS file under JUnit's temp directory. The helper reads credential provider entries before falling back to plain config. The tests verify no secret returns `""` rather than null and that `hasSecret` reflects non-empty resolution.

Dependencies and integration points: This is the credential source for `LangChain4jDispatcher` and chatbot provider availability. It integrates Recon chatbot config keys with Hadoop's credential provider mechanism, which is important for production deployments that should not store API keys in plaintext XML.

Risks: The JCEKS URI is built by string concatenation and assumes the local filesystem path format used by Hadoop credential providers. Tests do not cover malformed credential provider paths, provider initialization failures, or empty string secrets. Secret values are synthetic and not redacted in assertions because they are test-only.

Test signals: Exact returned secret from JCEKS; exact returned plaintext fallback; empty string and `hasSecret=false` for missing key; JCEKS overriding plaintext for the same key; and successful independent lookup of OpenAI and Gemini keys from one JCEKS store.
