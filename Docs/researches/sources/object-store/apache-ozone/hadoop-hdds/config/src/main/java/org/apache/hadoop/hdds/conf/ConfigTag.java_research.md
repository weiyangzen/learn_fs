# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigTag.java

## Purpose
Central enum of system-supported configuration tags used to categorize Ozone configuration properties.

## Important APIs, Types, And Functions
Values cover security, storage, SCM, OM, datanode, Ratis, performance, management, crypto compliance, disk balancer, and related domains. `Enum.name()` is used when writing XML tags.

## Control Flow
`Config` annotations attach one or more tags to a field. `ConfigFileAppender` joins the enum names into the generated `<tag>` element.

## State And Persistence
Enum constants are static metadata only; generated XML persists their names as strings.

## Dependencies And Integration Points
Integrated with config annotations, generated default XML, and downstream documentation or filtering tools consuming Ozone config tags.

## Risks
Renaming or removing a tag changes generated XML and can break external documentation/filtering. Empty tag arrays are allowed and produce an empty tag element.

## Test Signals
Signals include generated XML tag content, config-doc tooling behavior, and compile failures for annotations using removed enum constants.
