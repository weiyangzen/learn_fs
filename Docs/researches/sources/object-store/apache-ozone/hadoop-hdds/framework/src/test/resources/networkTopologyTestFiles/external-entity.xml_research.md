# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/external-entity.xml

Purpose: XML security fixture containing an external entity declaration to test XXE hardening.

Important APIs/types/functions: Defines a `DOCTYPE` with entity `xxe` pointing to `file:///etc/passwd`, then uses `&xxe;` as a layer type.

Control flow: Parser input only. A secure parser should reject or ignore external entity expansion and fail validation rather than reading local files.

State and persistence behavior: Static resource; attempts to reference external file system content only if XML parser is insecure.

Dependencies and integration points: Consumed by network topology XML parser/security tests.

Risks: If parser features are misconfigured, this fixture could expose local file content during tests. It must remain in test resources only.

Test signals: Security regression signal for disabling external entity expansion.
