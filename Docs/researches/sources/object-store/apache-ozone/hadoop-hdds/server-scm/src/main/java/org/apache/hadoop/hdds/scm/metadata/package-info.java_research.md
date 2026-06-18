# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/package-info.java

Purpose: This package descriptor declares `org.apache.hadoop.hdds.scm.metadata` as the Storage Container Manager metadata layer. It is documentation-only code, but it anchors the package that contains SCM DB definitions, metadata-store implementation, and codecs used by server-side SCM persistence.

Important APIs and types: The file exports no classes or functions. Its only API-level effect is the package declaration and package Javadoc.

Control flow: There is no runtime control flow. Java tooling associates the package comment with the generated package documentation for metadata-layer classes.

State and persistence behavior: This file does not store state. Its package is associated with persistent SCM metadata components elsewhere, so the main integration signal is naming and package ownership rather than behavior.

Dependencies and integration points: It integrates only with Java package documentation generation and the compiler. Downstream classes in the same package provide RocksDB/table definitions and certificate/key codecs.

Risks: The main risk is documentation drift if the package grows beyond metadata-store concerns. Because it has no executable code, behavioral regressions come only from package relocation or deletion affecting source organization and generated docs.

Test signals: No direct tests are expected. Build compilation and Javadoc/package checks are sufficient signals.
