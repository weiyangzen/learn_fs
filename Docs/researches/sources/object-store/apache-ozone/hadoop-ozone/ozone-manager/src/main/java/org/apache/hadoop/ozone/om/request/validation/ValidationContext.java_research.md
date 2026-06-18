
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationContext.java

Purpose: Supplies validators with OM layout-version state and bucket layout lookup without exposing full OzoneManager.

Important APIs and types: Interface annotated `@InterfaceStability.Evolving`; methods `versionManager()` and `getBucketLayout(volume, bucket)`; static factory `of(LayoutVersionManager, OMMetadataManager)`.

Control flow: The factory returns an anonymous implementation that delegates version access to the provided version manager and bucket layout resolution to `OzoneManagerUtils.getBucketLayout`, including linked bucket source layout behavior.

State and persistence behavior: Holds references to version manager and metadata manager; no persistence.

Dependencies and integration points: Used by validation annotations/methods to make layout-version and bucket-layout decisions during request pre/post processing.

Risks: Bucket layout lookup may throw IO exceptions and validators must handle or propagate them. Tests should cover factory delegation, linked bucket layout behavior through mocked metadata, and version-manager state exposure.
