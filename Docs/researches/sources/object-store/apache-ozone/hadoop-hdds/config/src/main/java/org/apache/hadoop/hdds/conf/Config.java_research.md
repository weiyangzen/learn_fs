# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/Config.java

## Purpose
Runtime-retained field annotation marking a Java field as backed by an Ozone/Hadoop configuration property.

## Important APIs, Types, And Functions
Annotation members define the property `key`, `defaultValue`, human `description`, `ConfigType`, time and storage units, `ConfigTag[]`, and a `reconfigurable` flag.

## Control Flow
Reflection utilities scan fields with this annotation, choose explicit or auto-detected type conversion, read values from a `ConfigurationSource`, and write back through a `ConfigurationTarget`. The annotation processor also reads it when generating XML fragments.

## State And Persistence
The annotation has no runtime state, but its metadata is persisted into generated configuration XML and drives in-memory object injection.

## Dependencies And Integration Points
Integrated with `ConfigGroup`, `ConfigType`, `ConfigTag`, `ConfigurationReflectionUtil`, and `ConfigFileGenerator`.

## Risks
Misdeclared keys, defaults, or units can produce wrong runtime values. `reconfigurable=true` on final fields is rejected later by reflection checks, not by the annotation itself.

## Test Signals
Tests should cover injection for each supported type, generated XML entries, prefix validation through `ConfigGroup`, and reconfiguration only for fields with the flag set.
