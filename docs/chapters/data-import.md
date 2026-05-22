# Data import

This chapter provides a short overview of how data enters NORA. In practice, there are four common paths:

- query and retrieve from a remote PACS
- receive pushed DICOM data through `storescp`
- import files manually from local or mounted storage
- create a project from existing backend data

Which path you use depends on where the data currently lives and how automated the workflow should be.

## Common Import Paths

### Remote PACS query/retrieve

Use [PACS Querier](pacs-querier.md) when users should search a configured PACS source from the web interface and pull selected studies into NORA.

### Inbound DICOM receive

Use [PACS and storescp Setup](pacs-storescp-setup.md) when scanners or PACS systems should push DICOM data directly into NORA through configured receive nodes.

### Manual import

Use [Manual import](manual-import.md) when users import files from local workstations or mounted folders through the web interface.

### Existing backend data

Use [Create Project From Existing Data](create-project-from-existing-data.md) when data is already present on storage and you want to register it as a NORA project rather than re-import it file by file.

### Programmatic import

Use [Dicom import via HTTP POST](dicom-import-via-http-post.md) for scripted or external-system driven ingest.

## Access and Routing

Imports are not only about file transfer. They also depend on:

- which target project receives the data
- which users may import into that project
- whether project filters in `pacs.conf` route incoming studies automatically
- whether anonymization or queue handling is applied during import

For the access model, see [Projects, Users, and Rights](projects-users-and-rights.md). For the configuration details behind PACS receive and routing, see [PACS and storescp Setup](pacs-storescp-setup.md).
