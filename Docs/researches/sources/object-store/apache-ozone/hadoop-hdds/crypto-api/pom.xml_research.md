## sources/object-store/apache-ozone/hadoop-hdds/crypto-api/pom.xml

Purpose: Maven module descriptor for `hdds-crypto-api`, the HDDS cryptographic API artifact.

Important APIs/types/functions: Maven coordinates inherit parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact ID `hdds-crypto-api`, module name/description, and property `maven.test.skip=true`.

Control flow: Maven build metadata only. No dependencies are declared in this module.

State and persistence behavior: Defines build-time artifact identity and test-skip behavior; no runtime persistence.

Dependencies and integration points: Participates in the parent HDDS reactor as the API surface for cryptographic functions. Empty dependency section suggests interfaces/classes in the module are expected to avoid module-level external dependencies.

Risks and test signals: `maven.test.skip=true` means module-local tests are not run, which can hide API regressions unless covered by downstream modules.
