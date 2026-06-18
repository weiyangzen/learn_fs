# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/EncodingTypeObject.java

Purpose: `EncodingTypeObject` pairs a raw object/bucket listing string with an optional encoding type so JAXB adapters can decide whether to URL-encode it.

Important APIs and flow: it is an immutable value object with `getEncodingType`, `getName`, and `createNullable`, which returns null instead of wrapping a null name. `ObjectKeyNameAdapter` consumes it during XML marshalling.

State, dependencies, risks, and tests: state is immutable response data. It integrates with list-object fields such as prefix, delimiter, key, and start-after. Risks are callers passing unsupported encoding strings and null handling causing missing XML elements. Tests should cover null factory behavior and URL/non-URL adapter output.
