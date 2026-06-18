## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/security/CredentialHelper.java

Purpose: central singleton for resolving chatbot secrets from Hadoop credential providers, with plaintext configuration fallback for compatibility.

Important APIs/types/functions: `getSecret(String configKey)` reads `configuration.getPassword`, catches `IOException`, then falls back to `configuration.get`; `hasSecret` checks non-empty resolved values.

Control flow: JCEKS/Hadoop credential provider is attempted first. Empty or missing credential values fall through to plaintext config. Failures are warned and do not fail startup.

State and persistence: holds only injected `OzoneConfiguration`. It integrates with `LangChain4jDispatcher` provider registration and key resolution.

Risks: returned `String` copies secret material from `char[]`, making it harder to clear from memory. Fallback to plaintext can mask credential-provider misconfiguration. Logging includes config key names but not values. Tests should cover credential-provider success, provider IOException fallback, plaintext fallback, missing key empty result, and `hasSecret`.
