# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/datanode.types.tsx


Purpose: Legacy datanode enum and storage report types.

Important APIs/types/functions: Exports `DatanodeStateList`, `DatanodeState`, `DatanodeOpStateList`, `DatanodeOpState`, and `IStorageReport`.

Control flow/state/persistence: Type declarations and const lists only.

Dependencies/integration points: Used by legacy tables/cards and ACL/storage components. Lists correspond to Hadoop/Ozone protobuf enums noted in comments.

Risks/test signals: Backend enum additions require list updates. `IStorageReport` omits newer filesystem capacity fields present in V2 datanode fixtures.
