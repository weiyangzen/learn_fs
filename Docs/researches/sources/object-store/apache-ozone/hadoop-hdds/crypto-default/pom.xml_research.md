## sources/object-store/apache-ozone/hadoop-hdds/crypto-default/pom.xml

Purpose: Maven module descriptor for `hdds-crypto-default`, the default HDDS cryptographic implementation artifact.

Important APIs/types/functions: Maven coordinates inherit parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact ID `hdds-crypto-default`, module name/description, and property `maven.test.skip=true`.

Control flow: Maven build metadata only. No explicit dependencies are declared.

State and persistence behavior: Defines artifact identity and test-skip behavior; no runtime state.

Dependencies and integration points: Intended as default implementation counterpart to HDDS crypto API, integrated through the parent reactor.

Risks and test signals: No module-local tests are run and no dependencies are declared here, so correctness depends on implementation files elsewhere or downstream integration tests.
