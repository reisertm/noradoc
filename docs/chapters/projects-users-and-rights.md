# Projects, Users, and Rights

NORA manages data access primarily through projects. A user does not get broad access to all data on the system. Instead, the user is granted rights to one or more projects, and those project memberships determine which subjects, studies, files, processing options, and administration actions are visible in the interface.

This chapter is intended as an introduction to the access model. It explains the main concepts and how they relate to each other. More technical administration details are covered in [Administration Backend](administration-backend.md), [PACS and storescp Setup](pacs-storescp-setup.md), and [Slurm, Queues, and Jails](slurm-queues-and-jails.md).

#### The Basic Model

In practice, data access in NORA is organized around four layers:

- users
- projects
- rights
- data inside a project

A user account represents one person or service identity. A project is the main organizational and access boundary. Rights connect a user to a project and define what that user may do there. Once a user can access a project, the subject/study view, file browser, viewer, import paths, and project-specific tools operate within that project context.

That means the usual question is not “can this user see patient X anywhere on the platform?”, but rather “does this user have access to the project in which that data lives?”

#### Projects As Access Boundaries

Projects are more than folders. They are the main containers for:

- subject and study listings
- file storage and import organization
- project-specific naming and anonymization rules
- project-specific processing definitions
- project-specific user rights

If a user does not have access to a project, that project does not normally appear in the desktop project list and its subject/study table is not available. This is why project design matters: it is the primary way to separate cohorts, teams, workflows, and permissions.

For the data model inside a project, see [Projects and Subject/Studies](projects-and-subject-studies.md).

#### Users, Project Members, and Admins

There are two important admin levels in NORA:

- system admins
- project admins

A system admin has global administrative privileges across the platform. In the current code this is represented by the user property `isadmin=1`. System admins can see all projects and are not restricted by normal project membership checks.

A project admin is an ordinary user for the platform as a whole, but has admin rights inside a specific project. In that project, the user may manage project-specific settings such as user rights and other administrative actions that are limited to that project.

A normal project user can work inside a project according to the rights assigned there, for example read-only access, download rights, or batchtool access.

#### What a Rights Entry Contains

At the backend level, access is stored as rights entries that connect:

- a `username`
- a `project`
- a `role`
- a small JSON-like rights object

The most important role values are:

- `user`
- `admin`

The rights object is used for fine-grained switches inside a project. Common examples in the current implementation are:

- `readonly`
- `batchtool`
- `download`
- `deanonym`

Typical meaning:

- `readonly=on`: the user may view data but should not modify project content
- `batchtool=on`: the user may use processing and batch execution functions
- `download=on`: the user may download project data through the UI
- `deanonym=on`: the user may see identifying information in situations where the project otherwise anonymizes it

These rights should be understood as project-specific capabilities layered on top of project membership. A user first needs access to the project at all; the detailed rights then control what that user can do inside that project.

#### How Project Lists Are Built

When NORA loads the desktop, it collects the projects the current user may access and attaches the corresponding role and rights information. This becomes the project information used throughout the session.

Conceptually, the project list is built from:

- explicit rights for the current user
- optionally shared rights such as `<ANY>`
- guest/public rights for public access cases
- global admin override for system administrators

This is why different users can log into the same NORA instance and still see different project lists and different capabilities inside the same UI.

#### Read-Only, Download, and Deanonymization

Three rights are especially important for daily work:

- `readonly`
- `download`
- `deanonym`

`readonly` is the most important safety switch. If it is enabled, the project remains visible but mutating actions should be blocked. This is useful for reviewers, external collaborators, or clinical users who should inspect data without changing it.

`download` is independent from basic view access. A user may be allowed to browse files in NORA but not export them from the web interface unless download rights are explicitly enabled.

`deanonym` matters in projects where data is anonymized in the UI or during import. It allows selected users to see identifying information where the project configuration would otherwise hide it.

#### Public and Guest Access

NORA also supports public or guest-style access patterns. In the current implementation, projects can be made available to the guest/public user through dedicated rights entries. Shared links can then open data without giving the recipient full access to all normal user projects.

This is different from ordinary user membership:

- normal project membership is tied to a named user account
- public access is tied to guest/public rights and shared-link logic

So a share link does not mean that the recipient becomes a normal member of the project. It means the link is resolved through a more limited access path.

For link-level behavior, see [URL Calls and Sharedlinks](url-calls-and-sharedlinks.md).

#### Rights Beyond Normal Projects

Not every rights entry refers to an ordinary data project. NORA also uses special rights namespaces for system-adjacent features.

Common examples are:

- `PACS_<node>`
- `PACSQUERY_<node>`
- `QUEUE_<queue>`

These do not mean “the user may open a normal project called `QUEUE_gpu`”. Instead they mean:

- `PACS_<node>`: the user may send data to a configured PACS destination
- `PACSQUERY_<node>`: the user may use a configured PACS query/retrieve source
- `QUEUE_<queue>`: the user may submit jobs to a specific execution queue

This is an important design point in NORA: the same rights mechanism is reused for both ordinary data projects and selected platform capabilities.

#### Who Usually Configures Rights

Rights are usually configured by one of the following:

- a system administrator
- a project administrator
- setup scripts or backend helper functions

In the web administration tools, project admins can assign or remove project rights for users of their project. On the backend side, rights can also be created through helper functions such as the SQL/Matlab wrappers described in [Administration Backend](administration-backend.md).

#### Practical Consequences

When planning a NORA deployment, it helps to think in this order:

1. Decide which datasets belong in which projects.
2. Decide which users should be project admins and which should be regular users.
3. Decide which projects need read-only reviewers, download rights, or deanonymization exceptions.
4. Decide which users may use PACS destinations, PACS query nodes, or specific job queues.

If those four questions are clear, most of the rights model becomes straightforward.

#### Summary

The short version is:

- projects are the main access boundary
- users receive rights per project
- role `admin` gives project-level administrative power
- rights such as `readonly`, `batchtool`, `download`, and `deanonym` refine what a user may do
- the same mechanism is also reused for PACS and queue permissions

So when you think about data access in NORA, start with projects first and only then with the individual rights switches.
