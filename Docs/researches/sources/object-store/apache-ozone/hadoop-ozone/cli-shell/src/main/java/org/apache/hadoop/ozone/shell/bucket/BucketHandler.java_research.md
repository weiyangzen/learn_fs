## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketHandler.java

Purpose: base class for bucket commands that take exactly one bucket URI.

Important APIs and control flow: mixes in `BucketUri`; overrides `getAddress` to return the validated bucket address. Subclasses inherit `Handler.call` for client lifecycle and implement `execute(OzoneClient, OzoneAddress)`.

State and dependencies: parse-time address state only. Depends on `Handler`, `BucketUri`, and `OzoneAddress`.

Risks and test signals: all subclasses rely on `BucketUri.convert` to reject malformed bucket paths before execution. No direct tests in this subset.
