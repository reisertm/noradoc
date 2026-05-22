# Processing

This chapter provides a short overview of how NORA handles processing jobs. In day-to-day use, processing usually starts from one of three entry points:

- the Batchtool GUI
- backend CLI calls through `nora`
- Python, MATLAB, or notebook-based wrappers

All three approaches use the same core ideas: project-aware file selection, output-path generation, job submission, and log inspection.

## User-Facing Processing Workflow

Use [General](general.md) for the processing model and design principles.

Use [Batchtool](batchtool.md) for the visual workflow editor used to compose batches from multiple jobs.

Use [Jobs](jobs.md) for the job list, runtime states, and practical use of backend CLI calls inside batch jobs or shell jobs.

## Programmatic and Backend Processing

Use [Administration Backend](administration-backend.md) for:

- `nora` CLI usage
- selector syntax
- tag-based file selection
- Python wrappers
- MATLAB wrappers

Use [Jupyter Notebooks](jupyter-notebooks.md) when processing is launched or inspected from notebooks or notebook terminals.

## Scheduler and Sandbox Layer

Use [Slurm, Queues, and Jails](slurm-queues-and-jails.md) for queue configuration, scheduler mapping, and filesystem sandboxing.

Use [Interactive Development Services](interactive-development-services.md) for interactive jobs such as Jupyter or code-server, which build on the same queue and jail infrastructure.
