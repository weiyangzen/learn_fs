<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/dev-support/intellij/ozone-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/dev-support/intellij/ozone-site.xml

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/dev-support/intellij/ozone-site.xml_research.md`.

## Purpose
Hadoop/Ozone XML configuration for local developer or test execution; primary keys include ozone.default.bucket.layout, hdds.profiler.endpoint.enabled, ozone.scm.block.client.address, ozone.csi.owner. The file has 99 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
XML property/filter entries detected: `ozone.default.bucket.layout, hdds.profiler.endpoint.enabled, ozone.scm.block.client.address, ozone.csi.owner, ozone.csi.socket, ozone.scm.client.address, ozone.metadata.dirs, ozone.scm.names, ozone.om.address, ozone.scm.container.size, hdds.datanode.storage.utilization.critical.threshold, hdds.prometheus.endpoint.enabled, ozone.recon.address, ozone.recon.db.dir`.

## Control Flow
The file is consumed declaratively by Hadoop configuration loaders, IntelliJ run configs, or SpotBugs tooling; no executable control flow exists inside the file.

## State And Persistence Behavior
Configuration state is static XML data; effects appear when the consuming tool loads these keys, exclusions, or local cluster settings.

## Dependencies And Integration Points
configuration keys `ozone.default.bucket.layout`, `hdds.profiler.endpoint.enabled`, `ozone.scm.block.client.address`, `ozone.csi.owner`, `ozone.csi.socket`, `ozone.scm.client.address`, `ozone.metadata.dirs`, `ozone.scm.names`.

## Risks And Edge Cases
- Configuration typos are usually detected only when the consuming tool starts.
- Static-analysis exclusions can hide real defects if they become broader than intended.

## Test Signals
Signal comes from the consuming configuration/static-analysis tool successfully loading the XML and honoring the declared keys or filters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/dev-support/intellij/ozone-site.xml -->
