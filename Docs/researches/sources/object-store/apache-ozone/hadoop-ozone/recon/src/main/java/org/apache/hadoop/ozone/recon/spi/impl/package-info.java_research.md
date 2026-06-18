# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/package-info.java

Purpose: Package documentation for Recon SPI implementations.

Important APIs/types: no executable APIs. The file declares package `org.apache.hadoop.ozone.recon.spi.impl` and documents that classes here provide connectivity to underlying Ozone subsystems.

State and persistence: none.

Dependencies and integration: indirectly covers provider implementations such as Recon DB, OM, SCM, JMX, and Prometheus providers. It helps Javadoc readers distinguish SPI implementation classes from interfaces in the sibling package.

Risks: low runtime risk. The main maintenance risk is documentation drift if package responsibilities expand beyond service provider implementations.

Test signals: none needed beyond compilation and license checks.
