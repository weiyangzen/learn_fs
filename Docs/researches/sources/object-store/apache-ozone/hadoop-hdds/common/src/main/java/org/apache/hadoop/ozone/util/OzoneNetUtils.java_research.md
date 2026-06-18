# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/OzoneNetUtils.java

## Purpose

`OzoneNetUtils` contains network utility methods for local-address detection and JVM DNS cache control, especially for Kubernetes deployments where pod FQDNs may not resolve at service startup.

## APIs and control flow

`disableJvmNetworkAddressCacheIfRequired` reads `ozone.jvm.network.address.cache.enabled` and, when disabled, sets JVM security properties for positive and negative DNS TTL to `0`. `isAddressHostNameLocal` compares the first label of an address host name to Hadoop `NetUtils.getLocalHostname()`. `getAddressWithHostNameLocal` rewrites an FQDN socket address to first-label hostname plus original port. `isAddressLocal` checks resolved local addresses. The boolean overloads switch behavior based on flexible FQDN resolution.

## State, dependencies, and integration

The class is stateless but mutates JVM-wide `Security` DNS cache properties. It depends on Ozone config keys, `OzoneConfiguration`, Hadoop `NetUtils`, and SLF4J. It integrates with service endpoint validation and HA/FQDN handling.

## Risks and test signals

Changing DNS cache properties is JVM-global and can affect unrelated code. Hostname matching by first label can misclassify hosts in unusual naming schemes. Tests should cover nulls, unresolved addresses, flexible-resolution branches, FQDN rewriting, and DNS property changes under configuration.
