## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/HddsDatanodeServiceProvider.java

Purpose: marker interface intended as an SPI abstraction for accessing DataNode endpoints from Recon.

Important APIs and types: declares no methods.

Control flow: none in this file.

State and persistence: none.

Dependencies and integration points: currently only a type placeholder. Future implementations could be bound through Guice like the OM, SCM, and metrics providers.

Risks and edge cases: an empty SPI can confuse readers because it defines no contract. Adding methods later will be a source-compatible but implementation-breaking change for any classes that already implement it.

Test signals: no tests apply until behavior is added.
