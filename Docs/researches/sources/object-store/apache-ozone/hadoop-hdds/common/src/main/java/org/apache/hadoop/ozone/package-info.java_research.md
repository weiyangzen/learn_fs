# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/package-info.java

## Purpose

This package descriptor describes the top-level `org.apache.hadoop.ozone` package in this module as containing datanode-side implementation support, especially container classes for persisting Ozone objects.

## APIs and integration

The file has no executable API. It provides JavaDoc context for the broader package and points readers toward container-related subpackages.

## State, dependencies, risks, and test signals

There is no state or persistence behavior. The main risk is outdated wording as the package grows beyond datanode/container support. Compile and JavaDoc checks validate syntax.
