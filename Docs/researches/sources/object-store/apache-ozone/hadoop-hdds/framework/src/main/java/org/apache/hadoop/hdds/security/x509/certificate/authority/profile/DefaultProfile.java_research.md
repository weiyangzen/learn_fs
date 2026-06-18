# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultProfile.java

## Purpose

`DefaultProfile` is the default Ozone PKI profile for non-CA certificates. It defines supported general names, supported X.509 extensions, key-usage constraints, and validation routines used during CSR approval.

## Important APIs, Types, and Functions

Supported general names are DNS, IP address, and otherName. Supported extensions include key usage, SAN, authority key identifier, extended key usage, and logo type. Static validators enforce key usage subset, SAN non-critical status and allowed general names, and non-critical extended key usage limited to serverAuth/clientAuth. Public `PKIProfile` methods expose supported names/extensions, validation, key usage, RDN handling, and `isCA()` status.

## Control Flow

`DefaultApprover` calls `validateRDN` for subject entries and `validateExtension` for each CSR extension. `validateExtension` rejects unsupported OIDs and delegates to the extension-specific predicate in the map.

## State and Persistence Behavior

The profile holds per-instance sets for general name and extended-key-purpose membership. The extension validator map is static and protected, so subclass mutations affect all instances.

## Dependencies and Integration Points

It uses BouncyCastle ASN.1 X.509 classes, Apache Commons `DomainValidator`, hex decoding for IP addresses, and SLF4J logging. It supplies policy to the default CA approver.

## Risks and Edge Cases

IP validation assumes BouncyCastle string values begin with `#` and are hex encoded. DNS validation uses public domain validation, which may reject cluster-local hostnames. RDN validation currently allows everything. The static map design makes extension support mutable across profiles.

## Test Signals

Cover key-usage subset behavior, SAN critical rejection, DNS/IP/otherName validation, malformed IP hex, unsupported extension rejection, extended-key-usage critical rejection, and profile interaction with `DefaultCAProfile`.
