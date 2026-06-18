# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.ozone.conf` as the package for Ozone configuration classes.

## APIs and integration

It has no executable API. In this subset it groups `OzoneServiceConfig`, which is consumed by shutdown management and HDDS configuration binding.

## State, dependencies, risks, and test signals

No state or persistence behavior exists. JavaDoc/compile validation is sufficient; the only practical risk is stale package documentation.
