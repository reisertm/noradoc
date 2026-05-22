# Jobs

#### Generic jobs

There are a multitude of predefined algorithms (mostly MATLAB) in NORA; however you can also implement your own scripts directly by using generic jobs. Currently there are three types of languages possible:

- **BASH**
- **Python**
- **MATLAB**

A generic jobs basically provides a field where you can enter simple expression or a full script in BASH/Python or MATLAB. Arguments from NORA are passed to the script by simple variable naming conventions.

For **BASH/Python** scripts input files (and all other parameters) are referenced by variables with a $-prefix with a special naming convention. For example, file arguments are referenced by $f1-$f9. Once NORA finds such an expression it automatically adds a corresponding row at the bottom of the job, which can be filled by the appropriate file patterns. The same holds of output arguments (represented by $o1-$o9) and output paths (prefix 'p'). Other parameters (STRING,NUMERIC) are referenced by prefixes 's' and 'n'.

In **MATLAB** the approach is a little bit different. You can manually add input/output arguments by using the "plus" sign and refer to the arguments by ordinary MATLAB variables. As input you have a series of cell-Arrays (input1, ..., inputN), as output a series of strings (output1, ..., outputN).

The input and output filenames are resolved to absolute paths that may be used directly.

For BASH and Python jobs it is often useful to call the NORA backend CLI `nora` directly from within the job. This gives access to project-aware file selection, tagging, metadata export, output-path computation, and other backend functions described in [Administration Backend](administration-backend.md).

![image-1601211287963.png](../assets/images/gallery/2020-09/image-1601211287963.png)

##### **Figure 4: Generic Jobs**

The Nora backend and related software is available to the jobs. The backend command is named `nora`.

Typical use cases inside BASH or Python jobs are:

- resolve additional project files with `nora -s ...`
- compute managed output locations with `nora --out ...`
- add or remove file tags with `nora --addtag ...` or `nora --rmtag ...`
- export metadata with `nora --exportmeta ...`

For example:

```bash
nora --addtag mytagname -s "$DPXpsid" "$f1"
```

This adds a tag to the file selected for processing. If the project context is already available through `DPXproject`, `-p MYPROJECT` can usually be omitted. For selector syntax and further examples, see [Administration Backend](administration-backend.md).
