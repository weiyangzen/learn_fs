# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/webapps/datanode/dn.js

## Purpose
`dn.js` drives the legacy Datanode web overview page. It fetches DataNode and Ozone DataNode JMX beans, normalizes a few JSON-string fields, and renders the Dust template named `dn` into the overview tab.

## Important APIs, Types, And Functions
The script is an immediately invoked function expression using strict mode. It keeps a shared `data` object initialized as `{ozone: {enabled: false}}`.

`loadDatanodeInfo()` calls `/jmx?qry=Hadoop:service=DataNode,name=DataNodeInfo`, converts the first bean with `workaround`, sets `HostName` from `DatanodeHostname`, and renders. `loadOzoneScmInfo()` queries `Hadoop:service=OzoneDataNode,name=SCMConnectionManager` and stores `SCMServers` when a bean exists. `loadOzoneStorageInfo()` queries `Hadoop:service=OzoneDataNode,name=ContainerLocationManager` and stores `LocationReport`. `workaround(dn)` parses `VolumeInfo` and `BPServiceActorInfo`; it converts the `VolumeInfo` object map into an array while injecting each map key as `name`. `render()` creates a Dust base with `helper_relative_time`, renders template `dn`, and writes the result into `#tab-overview`. `show_err_msg()` displays a generic failure message.

## Control Flow
On load, the script compiles `#tmpl-dn` into the Dust template registry, then fires all three AJAX requests. Each successful response mutates shared `data` and calls `render()`, so the overview can render multiple times as JMX calls return independently. Any failed request shows the alert panel.

## State And Persistence
State is browser-local and transient: the `data` object accumulates DataNode, SCM connection, and container location report fields for the current page load. The script persists nothing to server or local storage.

## Dependencies And Integration Points
Depends on jQuery (`$.get`, DOM writes), Dust templating, `dust.helpers.tap`, Moment.js, and Datanode JMX endpoints. The container-service Datanode `index.html` includes this script after Angular, NVD3, D3, Dust, and other static assets. It integrates with server-side JMX bean field names such as `VolumeInfo`, `BPServiceActorInfo`, `DatanodeHostname`, `SCMServers`, and `LocationReport`.

## Risks
The script assumes `resp.beans[0]` exists for the main DataNode query; an empty or malformed response will throw rather than show the friendly error. `JSON.parse` failures in `workaround` are not caught. The three asynchronous renders can show partially populated data and may overwrite DOM state repeatedly. `data.ozone.enabled` is initialized but never set true here, so template logic depending on it needs scrutiny. Error messages are generic and do not identify which JMX query failed.

## Test Signals
Browser or JS unit tests should mock each JMX endpoint, verify `VolumeInfo` map-to-array conversion, preserve `DatanodeHostname` as `HostName`, render correctly with staggered responses, and display the alert on failed requests. Integration tests should load the Datanode webapp with representative JMX beans and verify the overview tab populates SCM servers, storage report, volumes, and relative times.
