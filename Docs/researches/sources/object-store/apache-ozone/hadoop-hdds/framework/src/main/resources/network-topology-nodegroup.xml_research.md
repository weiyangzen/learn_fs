# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/network-topology-nodegroup.xml

## Purpose
This XML resource defines an alternate HDDS/Ozone network topology with an additional nodegroup layer between rack and node. It supports placement policies that need finer granularity than rack awareness.

## Important APIs, Types, And Functions
The configuration declares `<layoutversion>1</layoutversion>` and four layers: `datacenter` as `Root` with cost `1`; `rack` as `InnerNode` with prefix `rack`, cost `1`, and default `/default-rack`; `nodegroup` as `InnerNode` with prefix `ng`, cost `1`, and default `/default-nodegroup`; and `node` as `Leaf` with cost `0`. The topology path is `/datacenter/rack/nodegroup/node`, with `enforceprefix` set to false.

## Control Flow
SCM/network topology loading parses the layer table, then validates topology paths against the four-level path. When node locations omit inner layers, defaults can fill rack or nodegroup positions. Placement and distance calculations can then distinguish same nodegroup, same rack but different nodegroup, and cross-rack cases.

## State And Persistence
The file is static configuration. Parsed output becomes in-memory topology schema state; no runtime mutation or persistence is performed by the resource itself.

## Dependencies And Integration Points
SCM node manager tests reference `network-topology-nodegroup.xml`, and production code can select it through network topology configuration. It integrates with HDDS network topology classes that understand `Root`, `InnerNode`, and `Leaf` layer types.

## Risks
The extra nodegroup level changes distance/cost semantics and can alter replica placement decisions. Since `enforceprefix` is false, locations that do not start with `rack` or `ng` may still be accepted depending on parser behavior. Defaults include leading slashes, so normalization bugs can create duplicate or malformed topology paths.

## Test Signals
Tests should load the resource, validate four-layer path ordering, verify nodegroup defaults, check same-nodegroup versus same-rack distance behavior, and exercise SCM node registration with nodegroup locations. Existing `TestSCMNodeManager` references are important integration coverage.
