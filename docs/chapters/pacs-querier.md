# PACS Querier

This chapter describes the user-facing PACS query GUI. It assumes that a PACS query source has already been configured in `pacs.conf` and that the current user has permission to use it.

For the backend setup of `pacsquery`, `storescp`, receive nodes, and move-target configuration, see [PACS and storescp Setup](pacs-storescp-setup.md). For the related user-rights model, see [Projects, Users, and Rights](projects-users-and-rights.md).

### Starting the PACS Query Tool

To start the PACS query tool click on the wrench symbol in the upper left corner. Then click on PACS Query.

![starting_pacs_query.png](../assets/images/gallery/2022-02/starting_pacs_query.png)

### Overview of the Query Tool GUI

![query_gui.png](../assets/images/gallery/2022-02/query_gui.png)

In this window users can search for patients in the PACS.   
1\. Enter the patient data. The patient ID can be left empty. In the study date field there must at least be a `*` if the right date is not known. For `PatientName`, it is important that the last name is separated by a `^` from the first name. Depending on your PACS system it might be necessary to always use the full name, and abbreviations may not be accepted.  
2\. Start the search by hitting the Enter key or clicking on Run Search in the left menu.

### Patient Search in the Query Tool

![query_search.png](../assets/images/gallery/2022-02/query_search.png)

1\. On the left side you can see the different patients matching your search and the different visits or examinations that belong to them.   
2\. Here the different procedures and sequences are listed that you can import into NORA. If the sequence was acquired for more than one patient or examination, a number higher than 1 appears in the `inStudies` tab.

### Highlighting of Examinations for a Patient

![query_patient_highlight.png](../assets/images/gallery/2022-02/query_patient_highlight.png)

1\. To highlight which examinations belong to which patient click on the patient in the left table.  
2\. Then the examinations which were made during the selected visit of the patient are marked in the right table.

### Selection of the patients

![selection_patients_query.png](../assets/images/gallery/2022-02/selection_patients_query.png)

1\. First select the examinations you want to import by clicking on the box on the left.   
2\. In the left table, the number of examinations selected on the right is shown for each patient. You then have to select the patient by checking the box.  
3\. To start the import into NORA click on the button "pull selected".

### View of the imported Data

![view_query_import.png](../assets/images/gallery/2022-02/view_query_import.png)

1\. Now you can see your imported patient with the corresponding examinations.  
2\. If you click on the symbol the pseudonymization is deactivated and the real name of the patient is shown. So do not be surprised if the name initially displayed is not the real name.

## Related Topics

- Use [PACS and storescp Setup](pacs-storescp-setup.md) for PACS node setup and troubleshooting.
- Use [Projects, Users, and Rights](projects-users-and-rights.md) for PACS query and project access permissions.
- Use [Manual import](manual-import.md) if you want to import local files instead of querying a remote PACS.
