# Create Project From Existing Data

If you have direct access to the backend, all steps below should be done in a terminal there.

If you do not work directly on the backend host, first open a Jupyter connection or an SSH connection to a running NORA job and upload the data there, for example as a zip archive. For launching a Jupyter session, see [Jupyter Notebooks](../processing-and-ai/jupyter-notebooks.md). Place the extracted data into the project directory structure described below.

## Backend project location

Depending on your local environment, project data is stored in one of these locations:

- `[DATA]/username___yourprojectname`
- `[DATA]/yourprojectname`

The first form is typically used for user-owned projects. The second form is typically used for shared or global projects.

## Directory structure inside the project

The usual directory structure is:

```text
<pid>/<sid>
```

Here, `pid` is the patient ID and `sid` is the study ID.

Projects can use a different layout, so check the project-specific backend pattern before copying data. In the project settings, open `Project Management` and inspect the `json code` tab. The relevant fields are usually `regexp`, `hdr2subfolder`, and especially `patientfolderpattern`, for example `"<pid>/<sid>"`.

![Project-specific backend folder pattern in the `json code` view](../../assets/images/chapters/data-import/create-project-backend-folder-pattern.png)

## Copy the data

Copy your files into the matching location inside the project directory. Make sure the files end up in the exact folder structure expected by that project.

If you uploaded a zip archive to a backend-connected Jupyter or SSH session first, unpack it there and then move or copy the data into the final project path.

## Register the files in NORA

After the files are in place, add them to the NORA database from the backend terminal:

```bash
nora -p yourproject [DATA]/yourproject
```

Replace `yourproject` and `[DATA]` with the actual project name and data root on your system.
