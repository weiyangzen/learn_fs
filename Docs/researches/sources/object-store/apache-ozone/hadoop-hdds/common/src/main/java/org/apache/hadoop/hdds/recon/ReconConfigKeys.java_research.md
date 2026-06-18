# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfigKeys.java

## Purpose
Defines string and primitive constants for Recon service configuration shared by SCM, datanodes, and Recon clients. The class centralizes keys for Recon DB location and permissions, Recon RPC/HTTP/HTTPS addresses, datanode bind host and port, Prometheus endpoint, heatmap provider and enablement, administrator users/groups, and Recon task safemode wait threshold.

## Important APIs, Types, And Functions
`ReconConfigKeys` is a final constants holder with a private constructor. There are no methods beyond construction prevention. Important constants include `RECON_SCM_CONFIG_PREFIX`, `OZONE_RECON_DB_DIR`, `OZONE_RECON_ADDRESS_KEY`, `OZONE_RECON_HTTP_ADDRESS_KEY`, `OZONE_RECON_HTTPS_ADDRESS_KEY`, `OZONE_RECON_DATANODE_ADDRESS_KEY`, `OZONE_RECON_PROMETHEUS_HTTP_ENDPOINT`, and admin ACL keys.

## Control Flow
There is no runtime control flow. Consumers import constants to read or document configuration values through Ozone's configuration framework.

## State And Persistence
The class persists no state. The constants name external configuration persisted in XML/env/config sources and interpreted by Recon, SCM, datanode, and web-service startup code.

## Dependencies And Integration Points
It integrates with `OzoneConfigKeys` for administrator semantics in Javadocs and with any code that binds Recon ports, initializes Recon databases, or gates admin-only Recon APIs.

## Risks And Test Signals
Risk is compatibility drift: renaming values or defaults changes deployed config behavior. Test signals are configuration-key lookup tests, web/RPC bind tests, Recon DB permission tests, and admin ACL coverage.
