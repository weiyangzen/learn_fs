# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/OzoneClientConfig.java

Purpose: Configuration bean for Ozone client behavior, generated/documented by HDDS config annotations.

Important APIs/types/functions: Annotated with `@ConfigGroup(prefix = "ozone.client")`. It defines stream buffer sizes, datastream packet/window/sync settings, retry counts/intervals, checksum type and bytes per checksum, EC retry/queue/reconstruction pool settings, default bucket layout, HBase enhancement gates, streaming read settings, and checksum combine mode. `validate()` enforces consistency and mutates invalid settings to defaults where appropriate. Nested `ChecksumCombineMode`, `Keys`, and `Defaults` expose enum and stable test constants.

Control flow: Config injection sets fields from configuration. `@PostConstruct validate` checks positive buffer sizes, divisibility between max/flush/chunk sizes, minimum checksum size, HBase enhancement gate behavior, and streaming read sanity. Getters and setters expose fields to client components.

State and persistence behavior: Holds in-memory client configuration. It does not persist values itself, but annotations feed generated config documentation/metadata.

Dependencies and integration points: Used by stream output/input classes, checksum logic, EC code, bucket creation defaults, and HBase-related client features. Depends on `OzoneConfigKeys`, Guava preconditions, and HDDS config annotations.

Risks: Validation both rejects some invalid values and silently resets others with warnings; callers must ensure `validate()` has run when constructing manually. `getChecksumCombineMode()` returns null for invalid strings rather than defaulting. HBase enhancement settings are forcibly disabled unless allowed, which can surprise deployments if only subfeature flags are set.

Test signals: Config tests should cover divisibility failures, checksum minimum reset, HBase gate overrides, invalid stream read values, checksum combine parsing, and EC/HBase feature defaults.
