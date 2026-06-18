# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHANodeDetails.java

Purpose: `OMHANodeDetails` resolves OM HA configuration into local node details and peer node details. It supports explicit internal service IDs, multiple service IDs, listener nodes, flexible FQDN resolution, and non-HA fallback.

Important APIs and types: `loadOMHAConfig` is the main loader. Accessors return local details and peer map. Static helpers create non-HA or HA `OMNodeDetails` objects from service ID, node ID, RPC address, Ratis port, HTTP/HTTPS addresses, and listener status.

Control flow: The loader chooses candidate OM service IDs, reads active and listener node IDs for each service, reads RPC and Ratis addresses, resolves socket addresses, detects whether each address belongs to the local host unless an explicit node ID forces peer status, builds peer details, and returns when exactly one local match is found. If no node-specific OM address is configured, it falls back to default non-HA OM address. Configuration errors throw `OzoneIllegalArgumentException`.

State and persistence behavior: Instances are immutable references to local and peer node lists. The loader mutates the provided configuration by applying node-specific config overrides through `ConfUtils.setNodeSpecificConfigs`.

Dependencies and integration points: It is used during OM startup and Ratis ring construction. It depends on `OzoneConfiguration`, `OmUtils`, `ConfUtils`, `OzoneNetUtils`, Hadoop `NetUtils`, and `OMNodeDetails`.

Risks and test signals: Local address detection can be tricky with unresolved hosts, aliases, containers, and multi-homed nodes. Multiple local matches or no matches block startup. Tests should cover explicit node ID, multiple service IDs, listener nodes, unresolved flexible FQDN behavior, missing RPC address, non-HA fallback, duplicate local matches, and node-specific HTTP/HTTPS config substitution.
