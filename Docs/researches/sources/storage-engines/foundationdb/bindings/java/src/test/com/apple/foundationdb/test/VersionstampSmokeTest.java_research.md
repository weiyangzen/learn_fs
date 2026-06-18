# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/VersionstampSmokeTest.java

Purpose: smoke test for `SET_VERSIONSTAMPED_KEY` and transaction versionstamp retrieval in the Java tuple API.

Important APIs and flow: clears the tuple range for `prefix`, then runs a transaction that mutates a key packed with `Tuple.from("prefix", Versionstamp.incomplete()).packWithVersionstamp()` and returns `tr.getVersionstamp()`. A follow-up transaction reads the first key in the prefix subspace, unpacks it, and compares the embedded `Versionstamp` with `Versionstamp.complete(trVersion)`.

State and persistence: clears and writes keys under tuple prefix `prefix`. Dependencies include `MutationType.SET_VERSIONSTAMPED_KEY`, `Subspace`, `Tuple`, and `Versionstamp`. Risks include Java `assert` being disabled unless enabled with `-ea`, non-isolated prefix cleanup, and assuming one result key. Signal is printed versionstamps and assertion/equality when assertions are active.
