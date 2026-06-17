# Administration Backend

This chapter focuses on the Node.js command line interface `nora`, which is the main backend entry point for project administration, file selection, import, metadata export, and job launching.

The implementation referenced here is based on:

- `/nfs/norasys/unstable/src/node/nora.js`
- `/nfs/norasys/unstable/src/node/DPX_core.js`
- `/nfs/norasys/unstable/src/python/nora/DPX_core.py`

## CLI entry point

The executable lives in `src/node`:

```bash
export PATH=<path-to-nora>/src/node:$PATH
nora
```

Most commands operate on a project and therefore use `-p` or `--project`:

```bash
nora -p MYPROJECT --projectlist
```

You can omit `-p MYPROJECT` if the environment variable `DPXproject` is already set. The CLI also accepts a local `.dpx` file as a project fallback.

The CLI groups naturally into four areas:

- project and database administration
- file and tag management
- import and processing
- metadata export and integration helpers

## Important commands

### Project and database administration

- `--projectlist`
  Returns the visible projects.
- `--createproject NAME [MODULE]`
  Creates a project, optionally from a module definition such as `DEFAULT` or `BIDS`.
- `--updateproject NAME [MODULE]`
  Updates project settings from a module definition.
- `--createSQLuser PROJECT1 PROJECT2 ...`
  Creates a SQL user with project/global rights.
- `--deleteSQLuser JSONFILE`
  Deletes the SQL user described by a generated json file.
- `--sql "SQL"`
  Executes SQL directly and returns JSON. `--csv` switches to CSV output.
- `--changeID OLDPSID NEWPSID [DicomTag:Value] ...`
  Changes patient/study identifiers or anonymizes with `--anonym`.
- `--updatelinks FROMPROJECT PIZ1 PIZ2 ...`
  Repairs linked-file references after project path changes.
- `--maphash PID1 PID2 ...`
  Returns the SHA1-based anonymization mapping.
- `--sendmessage '{"channel":"platform,email",...}'`
  Sends platform or email notifications.
- `--admin ...`
  Dispatches to separate admin tools.

### File and tag management

- `--add FILE1 FILE2 ...`
  Registers files in the project.
- `--del FILE1 FILE2 ...`
  Deletes file rows.
- `--del_pat PID_OR_PSID ...`
  Deletes patients or studies.
- `--select ...` or `-s ...`
  Resolves file selectors.
- `--out ...`
  Computes an output location from a selector.
- `--pathout ...`
  Computes an output path without requiring an existing file row.
- `--addtag TAG1,TAG2 -s SELECTOR`
  Adds file tags to all selected files.
- `--rmtag TAG1,TAG2 -s SELECTOR`
  Removes file tags from all selected files.
- `--addtag_study TAG PSID`
  Adds a study tag.
- `--addtag_patient TAG PID`
  Adds a patient tag.
- `--tagstats`
  Summarizes tags in the project.

### Import and processing

- `--launch JSON`
  Launches a backend job from a JSON payload.
- `--launchfile JSONFILE`
  Same as `--launch`, but loads the payload from a file.
- `--launch_autoexec PSID`
  Starts the project's autoexecution pipeline for one study.
- `--import SRCPATH`
  Imports DICOM data into the project.
- `--batchimport SRCPATH`
  Iterates over subfolders and imports them as studies.
- `--importfiles SRCPATH REGEXP`
  Imports non-DICOM files matched by a regexp with named capture groups.
- `--dicomsend ...`
  Sends selected data to a target PACS.
- `--watch`
  Starts the watcher-based backend behavior.

### Metadata export and integration

- `--exportmeta PSID_SELECTOR FILE_SELECTOR --keys KEYSET`
  Exports metadata to CSV.
- `--importcsv CSVFILE IDCOL`
  Imports tabular metadata into the project.
- `--octave [COMMAND]`
  Starts Octave and runs `DPX_startup.m`.

## File selectors

The most important concept in the backend CLI is the file selector. `--select`, `--out`, `--exportmeta`, `--dicomsend`, and many batch functions depend on it.

In practice a selector has two parts:

1. a patient/study selector
2. one or more file selectors

The general shape is:

```bash
nora -p MYPROJECT -s '<subject-selector>' '<file-selector>'
```

Example:

```bash
nora -p MYPROJECT -s '10*' 'ROIS/mask*.nii.gz'
```

This means:

- match all patients whose patient ID starts with `10`
- within those studies, match files in `ROIS/` whose filename matches `mask*.nii.gz`

### Selector splitting rules

Selector strings are split on spaces, but quoted substrings are preserved. This matters when you pass several file selectors in one argument.

Example:

```bash
nora -p MYPROJECT -s 'stag:CTATX' 'cta_mni.nii.gz META/bolustiming.json'
```

This resolves the study selector `stag:CTATX` and then matches either:

- `cta_mni.nii.gz`
- `META/bolustiming.json`

Multiple file selectors are combined as a union, not an intersection.

### Subject selector forms

The first selector token defines which patients or studies are searched.

- `*`
  All patients.
- `12345`
  A patient ID match.
- `123*`
  Wildcard patient matching. `*` is translated to SQL `%`.
- `PID#SID`
  Restrict to one study of one patient.
- `PID#LATEST`
  Latest study of one patient.
- `PID#LATEST1`, `PID#LATEST2`, ...
  Latest study with SQL offset semantics.
- `PID#OLDEST`
  Oldest study of one patient.
- `PID#OLDEST1`, `PID#OLDEST2`, ...
  Oldest study with offset semantics.
- `stag:TAG`
  Select studies carrying study tag `TAG`.
- `notstag:TAG`
  Select studies that do not carry `TAG`.
- `ptag:TAG`
  Select patients carrying patient tag `TAG`.
- `tag:TAG`
  Alias for patient tag matching in the subject-selector position.
- `notptag:TAG`
  Exclude patients carrying `TAG`.
- `#tag:TAG`
  Select studies with study tag `TAG`.
- `PID#tag:TAG`
  Restrict to patient `PID` and study tag `TAG`.
- `SQL:...`
  Advanced mode. Injects a custom SQL `WHERE` condition used to select PSIDs.
- `PIDLIST:...`
  Advanced mode for an explicit patient list.
- `PSIDLIST:...`
  Advanced mode for an explicit study list.

### File selector forms

After the subject selector come one or more file selectors.

- `file.nii.gz`
  Match a filename in the study root.
- `SUBFOLDER/file.nii.gz`
  Match by subfolder and filename.
- `ROIS/*.nii.gz`
  Wildcards are allowed.
- `ABS:/absolute/path/file.nii.gz`
  Match one explicit absolute file path. If `--select` receives a single absolute path, the CLI rewrites it to this form automatically.
- `tag:TAG`
  Match files whose file-tag field contains `TAG`.
- `ftag:TAG`
  Explicit alias for file tags.
- `reading:FORMNAME[,extra SQL clauses]`
  Select reading results rather than normal files.
- `something_user_iter.reading`
  Alternate reading-result selector form.
- `[info]`
  Return study/patient information rows instead of file rows.

### Selector modifiers

The parser also accepts selector modifiers after the subject selector:

- `SORT` or `SORTASC`
  Sort ascending.
- `SORTDESC`
  Sort descending.
- `NTH(1)`
  Keep only the first match after sorting.
- `NTH(2)`
  Keep the second match.
- `NTH(-1)`
  Reverse after sorting and then pick the first entry of the reversed set.

Example:

```bash
nora -p MYPROJECT -s '12345#LATEST' 'META/*.json SORTDESC NTH(1)'
```

### JSON output modes

`--select` has two important output modifiers:

- `--json`
  Returns structured JSON instead of plain file paths.
- `--byfilename`
  Restructures the JSON per study and then per filename.

Example:

```bash
nora -p MYPROJECT --json --byfilename -s 'stag:CTATX' 'cta_mni.nii.gz META/bolustiming.json'
```

Without `--json`, the CLI prints one resolved path per line.

## Tags

NORA distinguishes three tag domains:

- file tags in `files.Tag`
- study tags in `studies.STag`
- patient tags in `patients.PTag`

All three are stored as slash-delimited strings such as:

```text
/baseline/qc_ok/
```

That representation explains the matching behavior:

- file tags are matched with `tag:TAG` or `ftag:TAG`
- study tags are matched with `stag:TAG`
- patient tags are matched with `ptag:TAG` or `tag:TAG` in the subject selector

Because tags are stored as slash-delimited segments, matching is intended to behave like exact tag membership rather than arbitrary substring matching.

### Adding and removing file tags

```bash
nora -p MYPROJECT --addtag qc_ok,reviewed -s '123*' 'ROIS/*.nii.gz'
nora -p MYPROJECT --rmtag reviewed -s '123*' 'ROIS/*.nii.gz'
```

The CLI resolves the selector first and then updates the `Tag` field of every matched file.

### Adding patient and study tags

```bash
nora -p MYPROJECT --addtag_study baseline 10001#20240512
nora -p MYPROJECT --addtag_patient training 10001
```

These commands modify `STag` and `PTag` respectively.

### Tagging during import

Import commands can apply tags while creating rows:

```bash
nora -p MYPROJECT --import /path/to/dicoms --addtag_study baseline --addtag_patient cohortA
```

This is especially useful for cohort curation and later selector-based processing.

## Import details

`--import` and `--batchimport` expose more than just basic DICOM conversion. Common options include:

- `--autoexec_queue [QUEUE]`
- `--handle_job_result`
- `--extrafiles_filter nii,hdr,img`
- `--nooverwrite`
- `--dcm2niix`
- `--keepdicom`
- `--anonym`
- `--anonym nohash`
- `--patients_id PIZ`
- `--studies_id SID`
- `--pattern "(?<studies_id>...)(?<patients_id>...)"`
- `--addtag_study TAG`
- `--addtag_patient TAG`

`--batchimport` additionally supports:

- `--range START END`
- `--fromfile FILEPATH`
- `--structured-with-filter`
- `--ConvolutionKernel ...`
- `--SliceThickness-Range START END`
- `--localizer-max-filecount N`
- `--timediff-range-days START END`
- `--pick-dates DD.MM.YYYY ...`
- `--pick-date-tolerance N`
- `--require-previous-pick`

## Metadata export

`--exportmeta` is the main CLI for extracting metadata from `nodeinfo.json`, files in `META/`, or other JSON outputs.

Example:

```bash
nora -p XYZ --exportmeta '*' 'nodeinfo.json' --keys '*'
```

Example with explicit JSON keys:

```bash
nora -p XYZ --exportmeta '*' 'META/radio*.json' --keys '*.mask.volume,*.mask.diameter'
```

Important behavior from the implementation:

- the first selector is the subject selector
- the second selector resolves the JSON-bearing files
- `--keys` accepts comma- or space-separated key sequences
- `Patient...` keys trigger inclusion of `nodeinfo.json`
- `file:PATH` can be used as the first selector to load PSIDs from a file

## Python wrappers

The Python wrappers in `/nfs/norasys/unstable/src/python/nora/DPX_core.py` are thin wrappers around the same CLI.

### `DPX_selectFiles`

```python
from nora.DPX_core import DPX_selectFiles

res = DPX_selectFiles("CTStroke", ["stag:CTATX", "cta_mni.nii.gz"])
```

Behavior:

- calls the Node CLI executable at `../../node/nora`
- always uses `--json --byfilename`
- accepts either a string selector or a two-element list
- returns nested JSON by default
- returns a flat file list when `aslist=True`

Examples:

```python
DPX_selectFiles("CTStroke", "cta_mni.nii.gz")
DPX_selectFiles("CTStroke", ["stag:CTATX", "cta_mni.nii.gz META/bolustiming.json"])
DPX_selectFiles("CTStroke", ["ptag:training", "ROIS/*.nii.gz"], aslist=True)
```

If `project=None`, the wrapper falls back to the environment variable `DPXproject`.

### `DPX_nora`

```python
from nora.DPX_core import DPX_nora

res = DPX_nora("MYPROJECT", ["--projectlist"])
```

This is the generic Python wrapper for arbitrary CLI calls that return JSON.

### `DPX_SQL_query`

```python
from nora.DPX_core import DPX_SQL_query

rows = DPX_SQL_query("MYPROJECT", "select * from patients limit 5")
```

This is a direct wrapper around `nora -p PROJECT --sql ...`.

### `DPX_getOutputLocation`

```python
from nora.DPX_core import DPX_getOutputLocation

out = DPX_getOutputLocation("MYPROJECT", "10001#20240512", "RESULTS/mask.nii.gz")
```

This wraps `--out` and expects a single absolute path result.

### `DPX_addFiles`

```python
from nora.DPX_core import DPX_addFiles

DPX_addFiles("MYPROJECT", ["/tmp/a.nii.gz", "/tmp/b.nii.gz"])
```

This is a direct wrapper around `--add`.

### `DPX_getMeta`

```python
from nora.DPX_core import DPX_getMeta

df = DPX_getMeta("*", "nodeinfo.json", project="MYPROJECT", keys="*")
```

Behavior:

- wraps `--exportmeta`
- always requests `--header_type full`
- returns a pandas `DataFrame`
- accepts extra raw CLI options via `params=[]`

### `DPX_loadAnnotation`

This helper reads NORA annotation JSON files and optionally converts them into a dictionary keyed by annotation name and point name.

## Practical examples

List all ROI masks for studies tagged `baseline`:

```bash
nora -p MYPROJECT -s 'stag:baseline' 'ROIS/*.nii.gz'
```

Return structured JSON for a patient-tagged cohort:

```bash
nora -p MYPROJECT --json --byfilename -s 'ptag:training' 'T1.nii.gz META/*.json'
```

Add a file tag to all matching outputs:

```bash
nora -p MYPROJECT --addtag checked -s '123*' 'RESULTS/*.nii.gz'
```

Export node info for all studies of one cohort:

```bash
nora -p MYPROJECT --exportmeta 'stag:cohortA' 'nodeinfo.json' --keys '*'
```

Use the same selector in Python:

```python
from nora.DPX_core import DPX_selectFiles

files = DPX_selectFiles("MYPROJECT", ["stag:cohortA", "nodeinfo.json"])
```

## Notes

- The selector implementation is SQL-backed. Wildcards are translated into SQL `LIKE` patterns.
- `--select` with a single absolute path is treated as an absolute-file lookup.
- Multiple file selectors are combined as a union.
- The current Python wrapper does not implement intersection semantics for multiple filenames.
- File selector behavior is defined in `translateFileQuery()` in `DPX_core.js`, so this is the canonical place to check when extending the syntax.

## MATLAB interface

The MATLAB layer remains useful for project setup, selector-based access, and output-path generation. Conceptually it mirrors the same backend ideas described above: choose a project, resolve selectors, and compute managed output locations.

### `DPX_Project`

`DPX_Project` selects or activates the current NORA project in MATLAB.

Typical use:

```matlab
DPX_Project('MYPROJECT')
```

This is usually the first command in a MATLAB session. Once the project is active, later calls such as `DPX_selectFiles` and `DPX_getOutputLocation` operate in that project context.

### `DPX_selectFiles`

`DPX_selectFiles` is the MATLAB-side file selector interface. It is the MATLAB equivalent of `nora -s ...` and follows the same general idea:

- the first part identifies patients or studies
- the second part identifies files within those studies

Typical examples:

```matlab
DPX_selectFiles('123* ROIS/*.nii.gz')
DPX_selectFiles('stag:baseline T1.nii.gz')
DPX_selectFiles('ptag:training META/*.json')
```

Use it when you want to:

- collect inputs for processing
- gather masks or derived outputs across a cohort
- query metadata-bearing JSON files for downstream analysis

The exact selector semantics in current backend development are defined most explicitly in the Node backend, so if behavior looks surprising, the selector rules documented above are the reference model.

### `DPX_getOutputLocation`

`DPX_getOutputLocation` computes the managed output location for a study and a target filename.

Typical use:

```matlab
out = DPX_getOutputLocation('10001#20240512','RESULTS/mask.nii.gz');
```

Use this when a MATLAB script should write results back into the NORA project structure in a predictable way instead of constructing paths manually.

This is especially important for:

- processing scripts that generate derived files
- batch jobs that write standardized outputs
- workflows that later re-query results using selectors

### `DPX_SQL_createProject`

`DPX_SQL_createProject` creates a project from MATLAB on the database side.

Typical use:

```matlab
DPX_SQL_createProject('MYPROJECT')
```

This is the MATLAB-side administrative entry point for creating a new project. In current workflows, project creation is often handled through the `nora` CLI with `--createproject`, but `DPX_SQL_createProject` remains relevant for MATLAB-driven administration scripts and older setup routines.

### MATLAB workflow summary

A typical minimal MATLAB workflow is:

```matlab
DPX_Project('MYPROJECT')
files = DPX_selectFiles('stag:baseline T1.nii.gz');
out = DPX_getOutputLocation('10001#20240512','RESULTS/example.nii.gz');
```

For project creation from MATLAB:

```matlab
DPX_SQL_createProject('MYPROJECT')
DPX_Project('MYPROJECT')
```
