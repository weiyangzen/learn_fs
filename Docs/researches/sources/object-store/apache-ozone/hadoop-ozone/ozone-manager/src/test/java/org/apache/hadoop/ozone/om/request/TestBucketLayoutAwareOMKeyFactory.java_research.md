# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestBucketLayoutAwareOMKeyFactory.java

Purpose: validates `BucketLayoutAwareOMKeyRequestFactory` mapping and reflective instantiation of `OMKeyRequest` implementations by command type and bucket layout.

Important APIs/types: `OM_KEY_REQUEST_CLASSES`, `getKey`, `addRequestClass`, `getRequestInstanceFromMap`, `OMKeyRequest`, `BucketLayout`, `Type`, `OMDirectoriesPurgeRequestWithFSO`, and protobuf `OMRequest`.

Control flow: `testGetRequestInstanceFromMap` iterates every mapping entry. Keys containing the FSO layout are instantiated with `BucketLayout.FILE_SYSTEM_OPTIMIZED`; other mappings are instantiated twice with `LEGACY` and `OBJECT_STORE`. Each instance is checked for matching bucket layout and counted. The test asserts expected counts: 15 FSO, 16 legacy, 16 OBS, and mapping-size consistency. `testAddInvalidRequestClass` registers an FSO purge-directories class under a factory key and asserts instantiation fails with `NoSuchMethodException` because the class lacks the required `(OMRequest, BucketLayout)` constructor.

State and persistence behavior: no DB state. It mutates the static request-class map in the invalid-class test, which can affect later tests if not isolated by JVM ordering or map overwrite behavior.

Dependencies and integration points: protects request factory coverage for OM key command handling across bucket layouts. Uses reflection and constructor contract as an integration point between factory registry and request classes.

Risks: hard-coded counts require updates when mappings change. Static map mutation can be order-sensitive. Key string inspection for FSO mapping assumes factory key format.

Test signals: catches missing constructors, wrong bucket layout injection, absent mappings, and count drift in key request factory registration.
