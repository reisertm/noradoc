# PACS and storescp Setup

This chapter explains how NORA is configured to:

- receive DICOM data from scanners or PACS via `storescp`
- query and retrieve data from remote PACS systems via `pacsquery`
- send data from NORA to remote PACS systems via `pacs`

The main configuration file for this is:

- `conf/pacs.conf`

The operational control layer is:

- `dpxcontrol`
- `nora --admin`

## A Primer: Basic DICOM communication concepts

Before looking at the NORA config, it helps to keep a few DICOM basics in mind.

### DICOM nodes

In network terms, a PACS, scanner, workstation, or NORA listener is a DICOM node. A node is simply a system that can participate in DICOM communication.

Typical examples are:

- a scanner that sends acquired series
- a hospital PACS that stores and serves studies
- a workstation that queries or retrieves studies
- a NORA `storescp` listener that receives incoming data

### AE title, host, and port

A DICOM node is usually identified by three pieces of information:

- AE title
- host or IP address
- port

The AE title is the logical DICOM application name. It is not the same thing as the hostname. In practice, remote PACS administrators often need exactly this tuple to register NORA as a sender, receiver, or move target.

### Push versus query/retrieve

There are two common ways imaging data reaches NORA:

1. push
2. query/retrieve

In a push workflow, a scanner or PACS sends images directly to a NORA receive node. In NORA, this is handled by `storescp`.

In a query/retrieve workflow, NORA first asks a remote PACS what studies exist and then requests delivery of selected data. In NORA, this is handled by `pacsquery`, typically using C-FIND and C-MOVE.

### Send, receive, and move target

These roles are easy to mix up:

- receive node
  A node that listens for incoming DICOM objects.
- send target
  A remote node to which NORA sends data.
- move target
  A receive node that a remote PACS is allowed to send data to after a C-MOVE request.

This is why NORA separates:

- `storescp` for receive nodes
- `pacs` for send targets
- `pacsquery` for query/retrieve definitions

### Why a dedicated move node is often useful

For PACS querying, a dedicated `movescu` receive node is often cleaner than reusing the normal inbound receive node. It gives you:

- a separate port
- a separate inbox folder
- clearer debugging when imports fail

That is the reason the config templates show a dedicated `NORA_MOVE`-style node for query/retrieve setups.

## Three different PACS-related sections

`pacs.conf` contains three different concepts that are easy to mix up:

- `storescp`
  Incoming DICOM listener nodes. These receive files pushed to NORA.
- `pacsquery`
  Remote query/retrieve definitions for `findscu` and `movescu`.
- `pacs`
  Remote send targets used when NORA sends data out to another PACS.

In short:

- `storescp` = receive into NORA
- `pacsquery` = search and pull from a remote PACS
- `pacs` = push from NORA to a remote PACS

## storescp: receiving data into NORA

The `storescp` block defines one or more DICOM listener nodes.

Example:

```js
storescp:
{
  NORA:
  {
    port:1200,
    timeout: 15
  }
}
```

Each entry is one listener node. The entry name such as `NORA` or `NORA_MOVE` is the logical node name in the config, not the network port itself.

### Important keys in `storescp`

#### `port`

The TCP port on which the listener accepts incoming DICOM associations.

Example:

```js
port:1200
```

This is the port that the sending PACS or modality must target.

#### `timeout`

The end-of-study timeout in seconds.

Example:

```js
timeout: 15
```

This controls when NORA considers one received study complete and triggers the import step. If this is too short, slow transfers can be split into multiple partial studies. If it is too long, imports are delayed.

Practical guidance:

- increase the timeout for slow links or large studies
- keep it shorter for local testing so imports finish quickly

#### `deleteafterimport`

Whether the received DICOM files are removed after import.

Example from the template:

```js
deleteafterimport: 0
```

Practical guidance:

- use `0` during first setup and debugging
- switch to deletion only after you are sure routing and import work correctly

#### `outputdirectory`

Optional custom folder for received DICOM files before import.

Example:

```js
outputdirectory:"$DPXROOT/var/import_from_movescu"
```

If you use a custom directory:

- it must exist
- `$DPXROOT` is expanded to the NORA root path
- if you use another absolute path, that path must also be present in the Docker mount configuration

This point is especially important when `DOCKER_run_storescp_in_docker=1`.

#### `type`

Optional mode selector:

- `storescp`
- `movescu`
- `both`

Typical meaning:

- `storescp`
  Pure receive node for pushed DICOM data.
- `movescu`
  Dedicated receive node used as move target for PACS query/retrieve.
- `both`
  Mixed use.

The template explicitly recommends using a dedicated `movescu` node if you use the PACS query/retrieve feature.

## How `dpxcontrol storescp` uses this config

`dpxcontrol storescp start` iterates over the `storescp` entries and launches one `storescp` process per entry.

Operational commands:

```bash
dpxcontrol storescp start
dpxcontrol storescp stop
dpxcontrol storescp restart
dpxcontrol storescp status
```

Equivalent:

```bash
nora --admin storescp start
```

### What the startup command does

The control script builds a `storescp` command roughly like this:

```bash
storescp -v -d -uf -fe .dcm --aetitle NORA --output-directory <importdir> ...
```

Important details from the implementation:

- `-uf -fe .dcm` stores incoming objects as files
- `--output-directory` is taken from `outputdirectory` or defaults to the instance import area
- the naming mode depends on `pacs_naming_scheme`
- after end-of-study, NORA triggers `htdocs/dicom/storescp_helper.php`

For normal receive nodes, `storescp_helper.php` creates the import trigger file that the daemon later picks up.

For nodes of type `movescu`, the helper call is suppressed because they are used as move targets for query/retrieve workflows.

## Project routing with `projectfilter`

Receiving data is only one half of the setup. After arrival, NORA decides into which project the data should be imported.

That is configured in:

```js
projectfilter:[ ... ]
```

Example:

```js
projectfilter:
[
  {
    targetProject: "INBOX",
    DCMPHPFilterString: " 1 == 1 "
  }
]
```

### How `projectfilter` works

Each rule contains:

- `targetProject`
  The import target project.
- `DCMPHPFilterString`
  A PHP expression evaluated against extracted DICOM header fields.

Rules are evaluated in order, and the logic stops at the first match. That means:

- put specific routing rules first
- put the fallback rule last

Example pattern from the comments:

```js
{
  targetProject: "INBOX",
  DCMPHPFilterString: "$hdr['InstitutionName'] == 'SomeInstitution' | $hdr['AETitle'] == 'SENDER' | $hdr['IssuerOfPatientID'] == 'XXX'"
}
```

Typical routing criteria are:

- institution name
- sender AE title
- issuer of patient ID
- other DICOM header values exposed in the helper logic

Practical guidance:

- start with a single default `INBOX` rule
- add more specific filters only after basic receive/import works
- keep the unconditional `1 == 1` rule last

## `pacsquery`: querying and pulling from a remote PACS

`pacsquery` defines remote PACS systems that NORA can search and retrieve from, typically through the PACS Querier GUI described in [PACS Querier](pacs-querier.md).

Example:

```js
pacsquery:
{
  MYPACS:
  {
    cfind : ' --aetitle NORA_MOVE --call <remoteaetitle> <ip> <port> ',
    cmove : ' --move NORA_MOVE --aetitle NORA_MOVE --call <remoteaetitle> <ip> <port> ',
    min_date_range:0,
    max_wait_time:60,
    storescp_folder: "$DPXROOT/var/import_from_movescu/"
  }
}
```

### Important keys in `pacsquery`

#### `cfind`

The command-line fragment used for DICOM C-FIND.

It defines:

- the local AE title used by NORA
- the remote called AE title
- remote PACS IP
- remote PACS port

#### `cmove`

The command-line fragment used for DICOM C-MOVE.

This must use a move target AE title that the remote PACS knows and trusts.

#### `storescp_folder`

The folder where incoming data from the move operation will arrive.

This must match the receive folder of the dedicated `movescu` `storescp` node.

That is the key setup rule for query/retrieve:

- the PACS query definition tells the remote system where to move the data
- the dedicated `storescp` node receives it
- the receive folder configured in both places must match

#### `min_date_range`

Limits overly broad searches, especially wildcard searches. This is mainly a safety setting to avoid huge accidental query results.

#### `max_wait_time`

Maximum time to wait for incoming data after a retrieve request.

Increase it for slow PACS systems or slow network links.

### Move target registration requirement

For C-MOVE to work, the remote PACS must know your move target.

The template states this explicitly: you must register the move target in the remote PACS as:

- `<aetitle> <ip> <port>`

Without this, the PACS may answer C-FIND correctly but fail to send images back.

### Default PACS Querier search

`pacsquery_defaultsearch` can prefill the GUI search form:

```js
pacsquery_defaultsearch:{"PatientID":12345678, PatientName:"Doe^John"}
```

This is mainly useful for testing.

## `pacs`: sending files from NORA to another PACS

The `pacs` block defines remote send targets for DICOM export from NORA.

Example:

```js
pacs:
{
  SELF:
  {
    aetitle: "NORA",
    researchprefix:"RESEARCH_"
  },
  NORATEST:
  {
    aetitle: "NORATESTNODE",
    ip: "127.0.0.1",
    port: "1200",
    allowedProjects:['*'],
    seriousSend:1
  }
}
```

### `SELF`

`SELF` has special meaning and is not just another target node.

It is used for instance-local send defaults, especially:

- `aetitle`
- `researchprefix`
- `defaultSeriesNumbers`

`defaultSeriesNumbers` allows fixed series numbers for known output types such as:

- `rcbf`
- `rcbv`
- `rtmax`
- `screenshots`

### Remote PACS targets

Regular target entries define:

- `aetitle`
- `ip`
- `port`
- `description`
- optional filters such as `DCMFilterInstitutionNames`
- `allowedProjects`
- `seriousSend`

Practical meaning:

- `allowedProjects` restricts which projects may send to that target
- `seriousSend` is used as a safety marker for real destinations

The project-level CLI uses these targets when calling DICOM send functionality.

## `pacs_naming_scheme`

The sample config contains:

```js
pacs_naming_scheme:"SIUID"
```

`dpxcontrol` uses this setting when launching `storescp`.

Current observed behavior:

- default naming mode uses `--sort-on-patientname`
- when `pacs_naming_scheme` is `SIUID`, the control script switches to `--sort-on-study-uid dpx`

This affects how incoming files are arranged on disk before import.

## `allow_open_in_pacsclient`

This is a specialized integration switch:

```js
allow_open_in_pacsclient: 0
```

It is described in the config as a custom specialty for a remote IMPAX opener. In most installations it can stay disabled unless that client integration is intentionally used.

## Minimal receive setup

For a basic inbound setup, you usually need:

1. a `storescp` node with a reachable port
2. a simple `projectfilter` default rule
3. `dpxcontrol storescp start`
4. a running daemon so the created import trigger files are processed

Minimal example:

```js
storescp:
{
  NORA:
  {
    port:1200,
    timeout:15,
    deleteafterimport:0
  }
},

projectfilter:
[
  {
    targetProject:"INBOX",
    DCMPHPFilterString:"1 == 1"
  }
]
```

Operationally:

```bash
dpxcontrol storescp start
dpxcontrol daemon start --nodejs
dpxcontrol storescp status
```

## Minimal PACS query/retrieve setup

For GUI-based PACS querying with retrieval, you usually need:

1. a dedicated `storescp` node for move-target reception
2. a matching `pacsquery` entry
3. registration of the move target AE title, IP, and port in the remote PACS
4. a running daemon

Example pattern:

```js
storescp:
{
  NORA_MOVE:
  {
    port:1201,
    timeout:15,
    outputdirectory:"$DPXROOT/var/import_from_movescu",
    type:"movescu"
  }
},

pacsquery:
{
  MYPACS:
  {
    cfind:' --aetitle NORA_MOVE --call REMOTEAE 10.0.0.5 104 ',
    cmove:' --move NORA_MOVE --aetitle NORA_MOVE --call REMOTEAE 10.0.0.5 104 ',
    storescp_folder:"$DPXROOT/var/import_from_movescu/"
  }
}
```

The key consistency check is:

- `storescp.outputdirectory` and `pacsquery.storescp_folder` must point to the same folder

## Docker-related setup notes

If your instance runs `storescp` inside Docker:

- check `DOCKER_run_storescp_in_docker` in `main.conf`
- make sure custom import folders are mounted into the container
- remember that changing ports or directories usually requires restart of the affected modules

The template and local config comments both emphasize that custom absolute directories must also be added to the Docker mount configuration.

## Testing and troubleshooting

### Check service state

```bash
dpxcontrol storescp status
dpxcontrol daemon status
```

### Start in debug mode

```bash
dpxcontrol storescp start --debug
```

This prints the underlying `storescp` command instead of quietly backgrounding it.

### Send a local test object

```bash
dpxcontrol test storescp
```

The control script sends a test DICOM file to `localhost:1200`, so this is most useful when your local receive node actually listens on port `1200`.

### Common setup failures

- port is not reachable from the sender
- timeout is too short and studies are split
- remote PACS does not know the C-MOVE target AE title, IP, and port
- `storescp_folder` and the move receive node folder do not match
- custom receive folders are not mounted into Docker
- no matching `projectfilter` rule sends data into the intended project
- daemon is not running, so receive files arrive but are not imported

## Relation to other documentation

Use this chapter for PACS and DICOM transport setup.

Use [PACS Querier](pacs-querier.md) for the user-facing query GUI.

Use [Configuration Files](configuration-files.md) for the broader config file overview.

Use [System Backend](system-backend.md) for the operational `dpxcontrol` command surface.
